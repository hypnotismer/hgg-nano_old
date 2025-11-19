from __future__ import print_function
import ROOT
from ROOT import TLorentzVector

ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

import math
import numpy as np


class VVVProducer(Module):
    def __init__(self, year):
        if "2016" in year:
            if "pre" in year.lower() or "apv" in year.lower():
                self.year = "2016pre"
            else:
                self.year = "2016post"
        elif "2017" in year:
            self.year = "2017"
        elif "2018" in year:
            self.year = "2018"
        else:
            raise ValueError("Unknown year: " + year)
        self.is_mc = None
        self.out = None
        self.leptons = None

    def beginJob(self):
        pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):

        self.leptons = []

        # Electron selection
        electrons = Collection(event, "Electron")
        nLooseElectron = 0  # pt>20, |eta|<2.5, mvaFall17V2Iso_WP90
        nTightElectron = 0  # pt>30, |eta|<2.5, mvaFall17V2Iso_WP80
        for iElectron in range(0, event.nElectron):
            passLooseElectron = electrons[iElectron].pt > 20 and abs(electrons[iElectron].eta) < 2.5 and electrons[iElectron].mvaFall17V2Iso_WP90
            passTightElectron = electrons[iElectron].pt > 30 and abs(electrons[iElectron].eta) < 2.5 and electrons[iElectron].mvaFall17V2Iso_WP80
            nLooseElectron += passLooseElectron
            nTightElectron += passTightElectron
            if passTightElectron:
                self.leptons.append(TLorentzVector())
                self.leptons[-1].SetPtEtaPhiM(electrons[iElectron].pt, electrons[iElectron].eta, electrons[iElectron].phi, electrons[iElectron].mass)

        # Muon selection
        muons = Collection(event, "Muon")
        nLooseMuon = 0  # pt>20, |eta|<2.4, looseId, pfRelIso04_all<0.25
        nTightMuon = 0  # pt>25, |eta|<2.4, tightId, pfRelIso04_all<0.06, |dxy|<0.05, |dz|<0.2
        for iMuon in range(0, event.nMuon):
            passLooseMuon = muons[iMuon].pt > 20 and abs(muons[iMuon].eta) < 2.4 and muons[iMuon].looseId and muons[iMuon].pfRelIso04_all < 0.25
            passTightMuon = muons[iMuon].pt > 25 and abs(muons[iMuon].eta) < 2.4 and muons[iMuon].tightId and muons[iMuon].pfRelIso04_all < 0.06 and abs(muons[iMuon].dxy) < 0.05 and abs(muons[iMuon].dz) < 0.2
            nLooseMuon += passLooseMuon
            nTightMuon += passTightMuon
            if passTightMuon:
                self.leptons.append(TLorentzVector())
                self.leptons[-1].SetPtEtaPhiM(muons[iMuon].pt, muons[iMuon].eta, muons[iMuon].phi, muons[iMuon].mass)

        # Check fatjet condition: at least one AK15Puppi with subJetIdx1>=0 and subJetIdx2>=0
        ak15Jets = Collection(event, "AK15Puppi")
        hasFatjet = False
        for ak15Jet in ak15Jets:
            if ak15Jet.subJetIdx1 >= 0 and ak15Jet.subJetIdx2 >= 0:
                hasFatjet = True
                break

        # Get MET
        met_pt = event.MET_pt

        # Apply selection criteria (union of 0L, 1L, 2L conditions)
        # 0L: no loose leptons, MET>100, has fatjet
        pass0L = (nLooseElectron == 0) and (nLooseMuon == 0) and (met_pt > 100) and hasFatjet

        # 1L: exactly one tight lepton (electron or muon), has fatjet
        pass1L = ((nTightElectron == 1) or (nTightMuon == 1)) and hasFatjet

        # 2L: at least two loose leptons (electrons or muons), has fatjet
        pass2L = ((nLooseElectron >= 2) or (nLooseMuon >= 2)) and hasFatjet

        # Return True if any of the conditions is satisfied
        return pass0L or pass1L or pass2L