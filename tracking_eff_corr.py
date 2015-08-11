# Tracking efficiency correction twiki page: https://twiki.cern.ch/twiki/bin/view/LHCb/LHCbTrackingEfficiencies

# The tracking efficiency is not directly measured in data. Instead, it is measured in MC and correction factors are
# applied afterwards. These correction factors are stored in files called ratio*.root. For each combination of data taking year, 
# Reco version and and Monte Carlo year, different factors are and different ratio*.files are needed. 
# However, as I am only using 2012 MC at the moment, I will just pretend that all my data and all my MC is 2012. 
# Once I start messing with 2011 MC, I will have another great number of things to think about. And on top of that, 
# there is no MC available with reco14, only reco12. 

# The correction factors for the tracking efficiency also include the correction on the cut efficiency of TRACK_CHI2NDOF, in order to solve
# two problems at once and also, I think, because it wouldn't be possible to measure two seperate correction factors.

# The ratio file for Reco14 2012 data vs 2012 MC is called ratio2012S20.root 
# I downloaded it from the twiki as I couldn't find it on AFS, where it was supposed to be available as well. 


import logging
import ROOT
import numpy
import root_pandas
from lhcbpythonmodules.root_tools.tree_tools import get_tree_dict


def calculateCorrectionFactor(mc_file_name, track_dict):

    temp         = ROOT.TFile.Open(track_dict["ratio-file"])
    factors      = temp.Get("Ratio")

    p_binning    = [edge*1000 for edge in list(factors.GetXaxis().GetXbins())]
    eta_binning  = list(factors.GetYaxis().GetXbins()) #sic
    # catching under-and overflow. I do not know if this is a good way of going forward, but it is done
    # in the effRatioDataOverMC script that is mentioned here https://twiki.cern.ch/twiki/bin/view/LHCb/TrackingEffRatio
    p_binning[0] = 0.
    eta_binning[0] = 0.
    p_binning[-1] = 1e7
    eta_binning[-1] = 1e2

    logging.debug(p_binning)
    logging.debug(eta_binning)

    root_mc_file = ROOT.TFile.Open(mc_file_name)
    data_frame = root_pandas.read_root(mc_file_name, get_tree_dict(root_mc_file).keys()[0], columns=[track_dict["p_name"],track_dict["eta_name"],track_dict["weights_name"]])

    hist, _, _ = numpy.histogram2d( data_frame[track_dict["p_name"]].values, 
                                    data_frame[track_dict["eta_name"]].values, 
                                    bins=[p_binning, eta_binning], 
                                    weights=data_frame[track_dict["weights_name"]].values
                                    )
    logging.debug("histogram:\n" + str(hist))

    correction = 1.
    error_squared = 0
    sum_hist_weights = 0
    for p_bin in range(0, len(p_binning)-1):
        for eta_bin in range(0, len(eta_binning)-1):
            sum_hist_weights += hist[p_bin][eta_bin]
            correction    +=     factors.GetBinContent(p_bin+1, eta_bin+1) * hist[p_bin][eta_bin]
            error_squared += pow(factors.GetBinError  (p_bin+1, eta_bin+1) * hist[p_bin][eta_bin], 2)
    error = numpy.sqrt(error_squared)
    correction /= sum_hist_weights
    error      /= sum_hist_weights

    logging.debug("total number of events: " + str(len(data_frame[track_dict["weights_name"]])))
    logging.debug("total weight of all events: " +  str(sum(data_frame[track_dict["weights_name"]])))
    logging.debug("total weight of all events in the histogram: " + str(sum_hist_weights))
    logging.debug("The difference is made up from events underflow or overflow the bins that are missing from the histogram.")
    logging.debug("These number are currently equal as I am catching the under- and overflow by extending the lowest and highest bin.")
    track_name = track_dict["p_name"]
    track_name = track_name[:track_name.find("_")]
    logging.info("correction factor for track {track}: {correction}".format(track=track_name, correction=correction))

    return correction, error




if __name__=="__main__":
    logger = logging.getLogger()
    console_handler = logging.StreamHandler()
    logger.setLevel(logging.INFO)
    logger.addHandler(console_handler)
