import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.common_cff import Var
from PhysicsTools.NanoTuples.ak15_cff import setupAK15
from PhysicsTools.NanoTuples.ak8_cff import addParticleNetAK8, getCustomTaggerDiscriminatorsAK8, addCustomTaggerAK8
from PhysicsTools.NanoTuples.pfcands_cff import addPFCands


def nanoTuples_customizeVectexTable(process):
    process.vertexTable.dlenMin = -1
    process.vertexTable.dlenSigMin = -1
    process.svCandidateTable.variables.ntracks = Var("numberOfDaughters()", int, doc="number of tracks")
    return process


def nanoTuples_customizeFatJetTable(process, runOnMC, addDeepAK8Probs=False):
    if addDeepAK8Probs:
        # add DeepAK8 raw scores: nominal
        from RecoBTag.ONNXRuntime.pfDeepBoostedJet_cff import _pfDeepBoostedJetTagsProbs
        for prob in _pfDeepBoostedJetTagsProbs:
            name = prob.split(':')[1]
            setattr(process.fatJetTable.variables, 'deepTag_' + name, Var("bDiscriminator('%s')" % prob, float, doc=prob, precision=-1))

        # add DeepAK8 raw scores: mass decorrelated
        from RecoBTag.ONNXRuntime.pfDeepBoostedJet_cff import _pfMassDecorrelatedDeepBoostedJetTagsProbs
        for prob in _pfMassDecorrelatedDeepBoostedJetTagsProbs:
            name = prob.split(':')[1]
            setattr(process.fatJetTable.variables, 'deepTagMD_' + name, Var("bDiscriminator('%s')" % prob, float, doc=prob, precision=-1))

    if runOnMC:
        process.finalGenParticles.select.append('keep+ (abs(pdgId) == 6 || abs(pdgId) == 23 || abs(pdgId) == 24 || abs(pdgId) == 25)')

    return process


def nanoTuples_customizeCommon(process, runOnMC, addAK15=True, addAK8=False, addPFcands=False,
                               keepLowPuppi=False, customAK8Taggers=[], customAK15Taggers=[]):
    pfcand_params = {'srcs': [], 'isPuppiJets':[], 'jetTables':[]}
    if addAK15:
        setupAK15(process, runOnMC=runOnMC, runParticleNet=False, runParticleNetMD=True, customAK15Taggers=customAK15Taggers)
        pfcand_params['srcs'].append('ak15WithUserData')
        pfcand_params['isPuppiJets'].append(True)
        pfcand_params['jetTables'].append('ak15Table')
    if addAK8:
        addParticleNetAK8(process, runParticleNet=False, runParticleNetMD=True)
        pfcand_params['srcs'].append('updatedJetsAK8WithUserData')
        pfcand_params['isPuppiJets'].append(True)
        pfcand_params['jetTables'].append('fatJetTable')
    if len(customAK8Taggers) > 0:
        tag_discs = sum([getCustomTaggerDiscriminatorsAK8(process, name) for name in customAK8Taggers], [])
        addCustomTaggerAK8(process, tag_discs)
        pfcand_params['srcs'].append('updatedJetsAK8WithUserData')
        pfcand_params['isPuppiJets'].append(True)
        pfcand_params['jetTables'].append('fatJetTable')
    if addPFcands:
        addPFCands(process, outTableName='PFCands', keepLowPuppi=keepLowPuppi, **pfcand_params)

    # nanoTuples_customizeVectexTable(process)
    # nanoTuples_customizeFatJetTable(process, runOnMC=runOnMC)

    return process


def nanoTuples_customizeData(process):
    process = nanoTuples_customizeCommon(process, False, addAK15=True, addAK8=False, addPFcands=False, customAK8Taggers=[], customAK15Taggers=['InclParticleTransformerAK15V2', 'InclParticleTransformerAK15V2-xggg'])

    process.NANOAODoutput.fakeNameForCrab = cms.untracked.bool(True)  # hack for crab publication
    process.add_(cms.Service("InitRootHandlers", EnableIMT=cms.untracked.bool(False)))
    return process


def nanoTuples_customizeMC(process):
    process = nanoTuples_customizeCommon(process, True, addAK15=True, addAK8=False, addPFcands=False, customAK8Taggers=[], customAK15Taggers=['InclParticleTransformerAK15V2', 'InclParticleTransformerAK15V2-xggg'])

    process.NANOAODSIMoutput.fakeNameForCrab = cms.untracked.bool(True)  # hack for crab publication
    process.add_(cms.Service("InitRootHandlers", EnableIMT=cms.untracked.bool(False)))
    return process


def nanoTuples_customizeZRTo3Glu(process):
    """Signal-only NanoAOD content needed to derive the AK15 Lund-plane calibration."""
    process = nanoTuples_customizeCommon(
        process, True, addAK15=True, addAK8=False, addPFcands=True, keepLowPuppi=True,
        customAK8Taggers=[],
        customAK15Taggers=['InclParticleTransformerAK15V2', 'InclParticleTransformerAK15V2-xggg'])

    process.finalGenParticles.select.append('keep++ abs(pdgId) == 32')
    process.zrTo3GluTruthTable = cms.EDProducer(
        'ZRTo3GluTruthTableProducer',
        src=cms.InputTag('finalGenParticles'),
        zrPdgId=cms.int32(32),
    )
    process.zrTo3GluTruthTask = cms.Task(process.zrTo3GluTruthTable)
    process.schedule.associate(process.zrTo3GluTruthTask)

    process.NANOAODSIMoutput.fakeNameForCrab = cms.untracked.bool(True)
    process.add_(cms.Service('InitRootHandlers', EnableIMT=cms.untracked.bool(False)))
    return process
