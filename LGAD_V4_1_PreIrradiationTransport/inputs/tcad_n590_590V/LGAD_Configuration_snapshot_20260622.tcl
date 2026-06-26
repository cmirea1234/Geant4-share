# Configuration File for Sentaurus TCAD SProcess
# Configuration File for LGAD Sensor
#
# Simulation Parameter
#
# ***Width Paramter***
# # JTE Width
set JTE_Width 10.0
# ***Parameter for Oxide***
# # etching / deposit type
set Deposit_Type "anisotropic"
set Etch_Type "anisotropic"
# # Thickness of Oxide
#set Oxide_Thickness 0.02
set Oxide_Thickness 0.03
#
# ***Parameter for Epi Wafer***
# # type of material
set Epi_material "Silicon"
# # type of deposition
set Epi_deposition_type "anisotropic"
# # thickness of deposition
set Epi_thickness 50.0
# # Ion type
set Epi_ion_type "Boron"
# # Doping Concentration
set Epi_concentration 3.0e12
#
# ***Parameter for Masking / PhotoResist (PR)***
# # Mask for p-gain
set pgain_Mask "pgain"
# # Location (left) for p-gain
set pgain_left 0.0
# # Location (right) for p-gain
set pgain_right 550.0
# # Mask for n+
set nplus_Mask "n+"
# # Location (left) for n+
set nplus_left 0.0
# # Location (right) for n+
set nplus_right 570.0
# # Mask for jte
set JTE_Mask "jte"
# # Location (left) for JTE
set JTE_left 570.0
# # Location (right) for JTE
set JTE_right 570.0+$JTE_Width
# # Mask for p-stop
set pstop_Mask "pstop"
# # Location (left) for p-stop
set pstop_left 610.0
# # Location (right) for p-stop
set pstop_right 620.0
# # Mask for guard-ring
set guardring_Mask "guard-ring"
# # Location (left) for guard-ring
set guardring_left 650.0
# # Location (right) for guard-ring
set guardring_right 715.0
# # Mask for oxide
set oxide_Mask "oxide"
# # Location (left) for oxide
set oxide_left 570.0+$JTE_Width/2
# # Location (right) for oxide
set oxide_right 650
# # Mask for cathode
set cathode_Mask "cathode"
# # Location (left) for cathode
set cathode_left 570.0+$JTE_Width/2
# # Location (right) for cathode
set cathode_right 650
# # Mask for oxide between contacts
set cathode_inverse_Mask "cathode_inverse"
# # Location (right) for oxide between contacts
set oxide_right 650
# ***Parameter for JTE (Junction Terminal Extension)***
# # Thikness of PR (PhotoResist) [micron]
set JTE_PR 3
# # implantation ion type
set JTE_ion "phosphorus"
# # implant energy for JTE [keV]
set JTE_Energy 400
# # dose for JTE [/cm-2]
set JTE_Dose 5.0e12
# # annealing temperature for JTE [Celcius]
set JTE_Temperature 1000
# # annealing time for JTE [second]
set JTE_time 1800
#
# ***Parameter for N-type guard-ring***
# # Thikness of PR (PhotoResist) [micron]
set guardring_PR 3
# # implantation ion type
set guardring_ion "phosphorus"
# # implant energy for guard-ring [keV]
set guardring_Energy 400
# # dose for guard-ring [/cm-2]
set guardring_Dose 5.0e12
# # annealing temperature for guard-ring [Celcius]
set guardring_Temperature 1000
# # annealing time for guard-ring [second]
set guardring_time 1800
#
# ***Parameter for p-gain layer***
# # Thikness of PR (PhotoResist) [micron]
set pgain_PR 5
# # implantation ion type
set pgain_ion "boron"
# # implant energy for p-gain [keV]
set pgain_Energy 600
# # dose for p-gain [/cm-2]
set pgain_Dose 2.5e12
# # annealing temperature for p-gain [Celcius]
set pgain_Temperature 900
# # annealing time for p-gain [second]
set pgain_time 3600
#
# ***Parameter for n+ layer***
# # Thikness of PR (PhotoResist) [micron]
set n_PR 3
# # implantation ion type
set n_ion "phosphorus"
# # implant energy for n+ [keV]
set n_Energy 40
# # dose for n+ [/cm-2]
set n_Dose 1.0e15
# # annealing temperature for n+ [Celcius]
set n_Temperature 900
# # annealing time for n+ [second]
set n_time 1800
#
# ***Parameter for p-stop layer***
# # Thikness of PR (PhotoResist) [micron]
set pstop_PR 3
# # implantation ion type
set pstop_ion "boron"
# # implant energy for p-stop [keV]
set pstop_Energy 300
# # dose for p-stop [/cm-2]
set pstop_Dose 7.5e12
# # annealing temperature for p-stop [Celcius]
set pstop_Temperature 850
# # annealing time for p-stop [second]
set pstop_time 1800
#
# ***Parameter for metal contact***
# # Type of metal
set contact_material "Aluminum"
# # Material between metals
set contact_oxide "SiO2"
# # Thickness of metal
set contact_thickness 1.0
# # Shape of contact
set contact_shape "box"