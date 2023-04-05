from rest_framework.views import APIView, status, Request
from rest_framework.response import Response
from .models import Pet
from groups.models import Group
from traits.models import Trait
from .serializers import PetSerializer
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404


class PetView(APIView, PageNumberPagination):
    def get(self, request):
        trait = request.query_params.get("trait")
        pets = Pet.objects.all()

        if trait:
            pets = pets.filter(traits__name__icontains=trait)

        result = self.paginate_queryset(pets, request)
        serializer = PetSerializer(result, many=True)

        return self.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = PetSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        group = serializer.validated_data.pop("group")
        tr_list = serializer.validated_data.pop("traits")

        find_group = Group.objects.filter(
            scientific_name__icontains=group["scientific_name"]
        ).first()

        if not find_group:
            find_group = Group.objects.create(**group)

        pet_obj = Pet.objects.create(
            **serializer.validated_data, group=find_group)

        for tr_dict in tr_list:
            tr_filter = Trait.objects.filter(
                name__iexact=tr_dict["name"]).first()

            if not tr_filter:
                tr_filter = Trait.objects.create(**tr_dict)

            pet_obj.traits.add(tr_filter)

        serializer = PetSerializer(pet_obj)

        return Response(serializer.data, status=201)


class PetDetailView(APIView):
    def get(self, _, pet_id):
        pet = get_object_or_404(Pet, id=pet_id)

        serializer = PetSerializer(pet)

        return Response(serializer.data)

    def patch(self, request, pet_id):
        pet = get_object_or_404(Pet, id=pet_id)

        serializer = PetSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        object_group = serializer.validated_data.pop("group", None)
        tr_list = serializer.validated_data.pop("traits", None)

        if object_group:
            try:
                group_found = Group.objects.get(
                    scientific_name=object_group["scientific_name"]
                )
            except Group.DoesNotExist:
                group_found = Group.objects.create(**object_group)

            pet.group = group_found

        if tr_list:
            tr_new = []
            for tr_dict in tr_list:
                tr_filter = Trait.objects.filter(
                    name__iexact=tr_dict["name"]
                ).first()

                if not tr_filter:
                    tr_filter = Trait.objects.create(**tr_dict)

                tr_new.append(tr_filter)

            pet.traits.set(tr_new)

        for key, value in serializer.validated_data.items():
            setattr(pet, key, value)

        pet.save()

        serializer = PetSerializer(pet)

        return Response(serializer.data)

    def delete(self, _, pet_id):
        pet = get_object_or_404(Pet, id=pet_id)

        pet.delete()

        return Response(status=204)
