import FWCore.ParameterSet.Config as cms

pfMassDecorrelatedHglugluV2DiscriminatorsJetTags = cms.EDProducer(
   'BTagProbabilityToDiscriminator',
   discriminators = cms.VPSet(
      cms.PSet(
         name = cms.string('probHggvsQCD'),
         numerator = cms.VInputTag(
            cms.InputTag('pfMassDecorrelatedHglugluV2JetTags', 'probHgg'),
            ),
         denominator = cms.VInputTag(
            cms.InputTag('pfMassDecorrelatedHglugluV2JetTags', 'probTTbarQCD'),
            cms.InputTag('pfMassDecorrelatedHglugluV2JetTags', 'probWJetsQCD'),
            ),
         ),
      cms.PSet(
         name = cms.string('probHggvsTopQCD'),
         numerator = cms.VInputTag(
            cms.InputTag('pfMassDecorrelatedDeepHglugluV2JetTags', 'probHgg'),

            ),
         denominator = cms.VInputTag(
            cms.InputTag('pfMassDecorrelatedHglugluV2JetTags', 'probTTbarQCD'),
            cms.InputTag('pfMassDecorrelatedHglugluV2JetTags', 'probWJetsQCD'),
            cms.InputTag('pfMassDecorrelatedDeepHglugluV2JetTags', 'probTTbarTop'),
            ),
         ),
      )
   )