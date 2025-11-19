import os
import sys
import optparse
import ROOT
import re

from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from PhysicsTools.NanoAODTools.postprocessing.analysis.VVVProducer import *



def main():
    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage)
    parser.add_option("--year", dest="year", help="which year sample", default="2018", type="string")
    parser.add_option("-m", dest="ismc", help="to apply sf correction or not", default=True, action="store_true")
    parser.add_option("-i", "--in", dest="inputs", help="input directory with files", default=None, type="string")
    parser.add_option("-o", "--out", dest="output", help="output directory with files", default="./", type="string")
    (opt, args) = parser.parse_args()

    if opt.ismc:

        if opt.year == "2016post":
            p = PostProcessor(opt.output, opt.inputs.rstrip(",").split(","), modules=[VVVProducer(opt.year)], provenance=True, fwkJobReport=True, outputbranchsel="keep_and_drop.txt")
        if opt.year == "2016pre":
            p = PostProcessor(opt.output, opt.inputs.rstrip(",").split(","), modules=[VVVProducer(opt.year)], provenance=True, fwkJobReport=True, outputbranchsel="keep_and_drop.txt")
        # Since btagSF errors have been fixed, btagSF has already been implement now.
        if opt.year == "2017":
            p = PostProcessor(opt.output, opt.inputs.rstrip(",").split(","), modules=[VVVProducer(opt.year)], provenance=True, fwkJobReport=True, outputbranchsel="keep_and_drop.txt")
        if opt.year == "2018":
            # Note that although PrefCorr() is used here, the prefire weight will not be used.
            p = PostProcessor(opt.output, opt.inputs.rstrip(",").split(","), modules=[VVVProducer(opt.year)], provenance=True, fwkJobReport=True, outputbranchsel="keep_and_drop.txt")

    else:
        year_list = ["UL2016_preVFPB", "UL2016_preVFPC", "UL2016_preVFPD", "UL2016_preVFPE", "UL2016_preVFPF", "UL2016F", "UL2016G", "UL2016H", "UL2017B", "UL2017C", "UL2017D", "UL2017E", "UL2017F", "UL2017G", "UL2017H", "UL2018A", "UL2018B", "UL2018C", "UL2018D"]
        if opt.year in ["UL2016_preVFPB", "UL2016_preVFPC", "UL2016_preVFPD", "UL2016_preVFPE", "UL2016_preVFPF"]:
            p = PostProcessor(opt.output, [opt.inputs], modules=[VVVProducer(opt.year)], provenance=True, fwkJobReport=True, outputbranchsel="keep_and_drop.txt")

        if opt.year in ["UL2016F", "UL2016G", "UL2016H"]:
            p = PostProcessor(opt.output, [opt.inputs], modules=[VVVProducer(opt.year)], provenance=True, fwkJobReport=True, outputbranchsel="keep_and_drop.txt")

        if opt.year in ["UL2017B", "UL2017C", "UL2017D", "UL2017E", "UL2017F", "UL2017G", "UL2017H"]:
            p = PostProcessor(opt.output, [opt.inputs], modules=[VVVProducer(opt.year)], provenance=True, fwkJobReport=True, outputbranchsel="keep_and_drop.txt")

        if opt.year in ["UL2018A", "UL2018B", "UL2018C", "UL2018D"]:
            p = PostProcessor(opt.output, [opt.inputs], modules=[VVVProducer(opt.year)], provenance=True, fwkJobReport=True, outputbranchsel="keep_and_drop.txt")

    p.run()


if __name__ == "__main__":
    sys.exit(main())