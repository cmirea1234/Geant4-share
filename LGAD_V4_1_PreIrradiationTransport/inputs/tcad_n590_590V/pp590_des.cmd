* Electrical Simulation : I-V and C-V of LGAD Sensor

File{
    Grid = "n23_590_fps.tdr"
    Current = "n590_LGAD_IV"
    Plot = "n590_LGAD_des.tdr"
    Output = "n590_LGAD_des.out"        
}

Electrode{
    {Name ="anode" Voltage=0.0 Material = "Aluminum"}
    {Name ="cathode" Voltage=0.0 Material = "Aluminum"}
}

Thermode{
    {Name="anode" Temperature=300 SurfaceConductance=0.1}
    {Name="cathode" Temperature=300 SurfaceConductance=0.1}
}

Physics{
    Fermi
    Temperature = 300
    AreaFactor = 1000
    Thermodynamic
    Mobility(
        DopingDependence
        HighFieldSaturation(GradQuasiFermi)
        Enormal(Lombardi)
    )
    Recombination(
        SRH(DopingDependence TempDependence)
        Auger(WithGeneration)
        Avalanche(Okuto)
    )
    EffectiveIntrinsicDensity(OldSlotboom)
}

Physics(Material="Silicon"){
    Fermi
    Temperature = 300
    Thermodynamic
    AreaFactor = 1000
    Mobility(
        DopingDependence
        HighFieldSaturation(GradQuasiFermi)
        Enormal(Lombardi)

    )
    Recombination(
        SRH(DopingDependence TempDependence)
        Auger(WithGeneration)
        Avalanche(Okuto)
    )
    EffectiveIntrinsicDensity(OldSlotboom)
}

Physics(MaterialInterface="Silicon/Oxide"){
    Traps((FixedCharge Conc=1.0e10)) 
}

Plot{
    hCurrent eCurrent hCurrent/Vector eCurrent/Vector
    eDensity hDensity
    eMobility hMobility
    eVelocity hVelocity
    
    ElectricField ElectricField/Vector Potential SpaceCharge
    
    Doping DonorConcentration AcceptorConcentration
    
    srhRecombination AugerRecombination AvalancheGeneration TotalRecombination NonLocal SurfaceRecombination
    
    eIonIntegral hIonIntegral MeanIonIntegral
    
    eAlphaAvalanche hAlphaAvalanche
    
    eGradQuasiFermi/Vector hGradQuasiFermi/Vector eEparallel hEparallel eEnormal hENormal
    
    BandGap BandGapNarrowing Affinity ConductionBand ValenceBand
}

Math{
    Iterations=20
    Number_Of_Threads=18
    Method=Blocked
    SubMethod=ParDiSo
    Extrapolate
    -CheckUndefinedModels
    CurrentWeighting
    ComputeIonizationIntegrals()
}

Solve{
    Coupled(LineSearchDamping = 0.4 Iterations=15){ Poisson }
    Coupled(LineSearchDamping = 0.4 Iterations=15){ Poisson Electron Hole }
    Quasistationary(
        InitialStep=1e-4 MinStep=1e-15 MaxStep=0.001
        Increment=2.0 Decrement=1.3
        Goal{Name="anode" Voltage=-590}
    ){Coupled{ Poisson Electron Hole }
    }
    Quasistationary(
        InitialStep=1e-4 MinStep=1e-15 MaxStep=0.02
        Increment=2.0 Decrement=1.2
        Goal{Name="anode" Voltage=-590}
    ){Coupled{ Poisson Electron Hole}
    }
}



