##lhcb_tracking_eff_correction

A quickly scripted no-warranty module for swiftly calculating the track efficiency
correction factor for a track in a monte carlo sample at LHCb.


The module defines a single function, `calculateCorrectionFactor(mc_file_name, track)` with the following parameters

 * `mc_file_name` : The name of the MC file in which contains the simulated tracks.
 * `track` : A dict describing relavant branches of the track who's reconstruction efficiency should be corrected. Here is an example:
    
       ```
       {
       "p_name"      : "muon_P",
       "eta_name"     : "muon_ETA",
       "weights_name" : "global_weight",
       "ratio-file" : "/path/to/ratio/file.root" #depends on cut on TRACK_CHI2
       }
       ```
