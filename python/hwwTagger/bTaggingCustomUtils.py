def updateSupportedBtagDiscr(supportedBtagInfos, supportedBtagDiscr, supportedMetaDiscr):
    
    ## Update taggers in DeepHWWV1, InclParticleTransformerV1, InclParticleTransformerV2
    from PhysicsTools.NanoTuples.hwwTagger.pfMassDecorrelatedDeepHWWV1_cff import _pfMassDecorrelatedDeepHWWV1JetTagsProbs, _pfMassDecorrelatedDeepHWWV1JetTagsMetaDiscrs
    from PhysicsTools.NanoTuples.hwwTagger.pfMassDecorrelatedInclParticleTransformerV1_cff import _pfMassDecorrelatedInclParticleTransformerV1JetTagsProbs, _pfMassDecorrelatedInclParticleTransformerV1JetTagsMetaDiscrs
    from PhysicsTools.NanoTuples.hwwTagger.pfMassDecorrelatedInclParticleTransformerV2_cff import _pfMassDecorrelatedInclParticleTransformerV2JetTagsProbs, _pfMassDecorrelatedInclParticleTransformerV2JetTagsMetaDiscrs, _pfMassDecorrelatedInclParticleTransformerAK15V2JetTagsProbs, _pfMassDecorrelatedInclParticleTransformerAK15V2JetTagsMetaDiscrs
    from PhysicsTools.NanoTuples.hwwTagger.pfMassDecorrelatedXgggFinetuneV2_cff import _pfMassDecorrelatedXgggFinetuneV2JetTagsProbs

    # update supportedBtagDiscr
    supportedBtagInfos.extend(["pfMassDecorrelatedDeepHWWV1TagInfos"])
    supportedBtagInfos.extend(["pfMassDecorrelatedInclParticleTransformerV1TagInfos"])
    supportedBtagInfos.extend(["pfMassDecorrelatedInclParticleTransformerV2TagInfos"])
    supportedBtagInfos.extend(["pfMassDecorrelatedXgggFinetuneV2TagInfos"])
    for disc in _pfMassDecorrelatedDeepHWWV1JetTagsProbs + _pfMassDecorrelatedDeepHWWV1JetTagsMetaDiscrs:
        supportedBtagDiscr[disc] = [["pfMassDecorrelatedDeepHWWV1TagInfos"]]
    for disc in _pfMassDecorrelatedInclParticleTransformerV1JetTagsProbs + _pfMassDecorrelatedInclParticleTransformerV1JetTagsMetaDiscrs:
        supportedBtagDiscr[disc] = [["pfMassDecorrelatedInclParticleTransformerV1TagInfos"]]
    for disc in _pfMassDecorrelatedInclParticleTransformerV2JetTagsProbs + _pfMassDecorrelatedInclParticleTransformerV2JetTagsMetaDiscrs:
        supportedBtagDiscr[disc] = [["pfMassDecorrelatedInclParticleTransformerV2TagInfos"]]
    for disc in _pfMassDecorrelatedInclParticleTransformerAK15V2JetTagsProbs + _pfMassDecorrelatedInclParticleTransformerAK15V2JetTagsMetaDiscrs:
        supportedBtagDiscr[disc] = [["pfMassDecorrelatedInclParticleTransformerAK15V2TagInfos"]]
    for disc in _pfMassDecorrelatedXgggFinetuneV2JetTagsProbs:
        supportedBtagDiscr[disc] = [["pfMassDecorrelatedXgggFinetuneV2TagInfos"]]
    # update supportedMetaDiscr
    for disc in _pfMassDecorrelatedDeepHWWV1JetTagsMetaDiscrs:
        supportedMetaDiscr[disc] = _pfMassDecorrelatedDeepHWWV1JetTagsProbs
    for disc in _pfMassDecorrelatedInclParticleTransformerV1JetTagsMetaDiscrs:
        supportedMetaDiscr[disc] = _pfMassDecorrelatedInclParticleTransformerV1JetTagsProbs
    for disc in _pfMassDecorrelatedInclParticleTransformerV2JetTagsMetaDiscrs:
        supportedMetaDiscr[disc] = _pfMassDecorrelatedInclParticleTransformerV2JetTagsProbs
    for disc in _pfMassDecorrelatedInclParticleTransformerAK15V2JetTagsMetaDiscrs:
        supportedMetaDiscr[disc] = _pfMassDecorrelatedInclParticleTransformerAK15V2JetTagsProbs

    return supportedBtagInfos, supportedBtagDiscr, supportedMetaDiscr

## Import TagInfos additional to RecoBTag_cff
from PhysicsTools.NanoTuples.hwwTagger.pfMassDecorrelatedDeepHWWV1_cff import *
from PhysicsTools.NanoTuples.hwwTagger.pfMassDecorrelatedInclParticleTransformerV1_cff import *
from PhysicsTools.NanoTuples.hwwTagger.pfMassDecorrelatedInclParticleTransformerV2_cff import *
from PhysicsTools.NanoTuples.hwwTagger.pfMassDecorrelatedXgggFinetuneV2_cff import *