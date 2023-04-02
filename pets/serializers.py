from rest_framework import serializers

from groups.models import Group
from groups.serializers import GroupSerializer
from pets.models import Pet
from traits.models import Trait
from traits.serializers import TraitSerializer


class PetSerializer(serializers.ModelSerializer):
    group = GroupSerializer()
    traits = TraitSerializer(many=True)

    class Meta:
        model = Pet
        fields = ['id', 'name', 'age', 'weight', 'sex', 'group', 'traits']

    def create(self, validated_data):
        group_data = validated_data.pop('group')
        traits_data = validated_data.pop('traits')

        group, _ = Group.objects.get_or_create(**group_data)
        pet = Pet.objects.create(group=group, **validated_data)

        traits = [Trait.objects.get_or_create(**trait_data)[0] for trait_data in traits_data]
        pet.traits.set(traits)

        return pet

    def update(self, instance, validated_data):
        group_data = validated_data.pop('group', None)
        traits_data = validated_data.pop('traits', None)

        if group_data:
            group, _ = Group.objects.get_or_create(**group_data)
            instance.group = group

        if traits_data:
            traits = [Trait.objects.get_or_create(**trait_data)[0] for trait_data in traits_data]
            instance.traits.set(traits)

        instance.update(**validated_data)

        return instance