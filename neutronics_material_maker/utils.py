#!/usr/bin/env python3

__author__ = "neutronics material maker development team"

import warnings

try:
    import openmc
except BaseException:
    warnings.warn(
        "OpenMC not found, .openmc_material, .serpent_material, .mcnp_material, .fispact_material not avaiable"
    )


def make_fispact_material(mat):
    """
    Returns a Fispact material card for the material. This contains the required keywords
    (DENSITY and FUEL) and the number of atoms of each isotope in the material for the given volume.
    The Material.volume_in_cm3 must be set to use this method. See the Fispact FUEL keyword
    documentation for more information https://fispact.ukaea.uk/wiki/Keyword:FUEL
    """

    if mat.volume_in_cm3 is None:
        raise ValueError(
            "Material.volume_in_cm3 needs setting before fispact_material can be made"
        )

    mat_card = [
        "DENSITY " + str(mat.openmc_material.get_mass_density()),
        "FUEL " + str(len(mat.openmc_material.nuclides)),
    ]
    for (
        isotope,
        atoms_barn_cm,
    ) in mat.openmc_material.get_nuclide_atom_densities().values():
        atoms_cm3 = atoms_barn_cm * 1.0e24
        atoms = mat.volume_in_cm3 * atoms_cm3
        mat_card.append(isotope + " " + "{:.12E}".format(atoms))

    return "\n".join(mat_card)


def make_serpent_material(mat):
    """Returns the material in a string compatable with Serpent II"""
    if mat.material_tag is None:
        name = mat.material_name
    else:
        name = mat.material_tag

    if mat.zaid_suffix is None:
        zaid_suffix = ""
    else:
        zaid_suffix = mat.zaid_suffix

    mat_card = ["mat " + name + " " +
                str(mat.openmc_material.get_mass_density())]
    # should check if percent type is 'ao' or 'wo'

    for isotope in mat.openmc_material.nuclides:
        if isotope[2] == "ao":
            prefix = "  "
        elif isotope[2] == "wo":
            prefix = " -"
        mat_card.append(
            "     "
            + isotope_to_zaid(isotope[0])
            + zaid_suffix
            + prefix
            + str(isotope[1])
        )

    return "\n".join(mat_card)


def make_mcnp_material(mat):
    """Returns the material in a string compatable with MCNP6"""

    if mat.material_id is None:
        raise ValueError(
            "Material.material_id needs setting before mcnp_material can be made"
        )

    if mat.material_tag is None:
        name = mat.material_name
    else:
        name = mat.material_tag

    if mat.zaid_suffix is None:
        zaid_suffix = ""
    else:
        zaid_suffix = mat.zaid_suffix

    mat_card = [
        "c     "
        + name
        + " density "
        + str(mat.openmc_material.get_mass_density())
        + " g/cm3"
    ]
    for i, isotope in enumerate(mat.openmc_material.nuclides):

        if i == 0:
            start = "M" + str(mat.material_id) + " "
        else:
            start = "     "

        if isotope[2] == "ao":
            prefix = "  "
        elif isotope[2] == "wo":
            prefix = " -"

        rest = isotope_to_zaid(isotope[0]) + \
            zaid_suffix + prefix + str(isotope[1])

        mat_card.append(start + rest)

    return "\n".join(mat_card)


def isotope_to_zaid(isotope):
    z, a, m = openmc.data.zam(isotope)
    zaid = str(z).zfill(3) + str(a).zfill(3)
    return zaid
