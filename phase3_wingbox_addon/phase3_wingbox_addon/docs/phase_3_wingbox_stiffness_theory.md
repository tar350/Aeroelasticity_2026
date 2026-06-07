# Phase 3 Theory: From Laminate ABD to Wingbox EI, GJ, and Bend-Twist Indicators

Phase 2 gave laminate stiffness matrices. Phase 3 converts those laminate-level properties into a simplified wingbox beam model.

## 1. Why this step matters

Aeroelasticity does not directly use only A, B, and D matrices. Wing-level aeroelastic calculations need beam-style stiffness quantities:

- EI: bending stiffness
- GJ: torsional stiffness
- Kbt: bending-torsion coupling

This phase estimates EI and GJ using a closed rectangular wingbox approximation.

## 2. Bending stiffness

The top and bottom skins act like bending caps separated by the wingbox height. The approximate bending stiffness is:

EI ≈ Σ E_i A_i z_i²

Material farther from the neutral axis contributes strongly to EI. This is why the upper and lower skins are important in a wingbox.

## 3. Torsional stiffness

For a thin-walled closed section, the Bredt-Batho torsion approximation is:

GJ = 4 A_m² / Σ[s/(G t)]

where A_m is the enclosed median area, s is panel length, G is effective shear modulus, and t is panel thickness.

## 4. Preliminary coupling indicator

This phase uses D16/D11 and D26/D22 as laminate-level coupling indicators. These are not yet a full anisotropic beam Kbt extraction. They tell us which laminates are more likely to generate bend-twist effects.

A later phase can replace this with a more rigorous cross-sectional stiffness extraction.

## 5. Interpretation

For each layup, compare:

- Mass
- EI
- GJ
- D16/D11 and D26/D22

A good aeroelastic tailoring candidate is not always the stiffest layup. The goal is a good balance of mass, bending stiffness, torsional stiffness, and useful bend-twist behavior.
