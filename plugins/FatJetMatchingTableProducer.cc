#include "PhysicsTools/NanoTuples/interface/FatJetMatching.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"
#include "FWCore/Utilities/interface/Exception.h"

#include "DataFormats/Common/interface/View.h"
#include "DataFormats/HepMCCandidate/interface/GenParticle.h"
#include "DataFormats/Math/interface/deltaR.h"
#include "DataFormats/NanoAOD/interface/FlatTable.h"
#include "DataFormats/PatCandidates/interface/Jet.h"

#include <algorithm>
#include <cmath>
#include <memory>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

class FatJetMatchingTableProducer : public edm::stream::EDProducer<> {
public:
  explicit FatJetMatchingTableProducer(const edm::ParameterSet &);
  ~FatJetMatchingTableProducer() override = default;

  static void fillDescriptions(edm::ConfigurationDescriptions &descriptions);

private:
  void produce(edm::Event &, const edm::EventSetup &) override;

  std::string normalizeLabelName(const std::string &) const;
  std::string applyHVV2DVarMassLabel(const std::string &, const deepntuples::FatJetMatching::FatJetMatchingResult &) const;
  int labelIndex(const std::string &) const;

  edm::EDGetTokenT<edm::View<pat::Jet>> jets_token_;
  edm::EDGetTokenT<reco::GenParticleCollection> gen_particles_token_;

  std::string name_;
  std::string label_name_;
  double jet_radius_;
  bool is_md_tagger_;
  bool is_hvv_2d_var_mass_sample_;
  deepntuples::FatJetMatching matcher_;
  std::unordered_map<std::string, int> label_to_index_;
};

FatJetMatchingTableProducer::FatJetMatchingTableProducer(const edm::ParameterSet &iConfig)
    : jets_token_(consumes<edm::View<pat::Jet>>(iConfig.getParameter<edm::InputTag>("src"))),
      gen_particles_token_(consumes<reco::GenParticleCollection>(iConfig.getParameter<edm::InputTag>("genParticles"))),
      name_(iConfig.getParameter<std::string>("name")),
      label_name_(iConfig.getParameter<std::string>("labelName")),
      jet_radius_(iConfig.getParameter<double>("jetRadius")),
      is_md_tagger_(iConfig.getParameter<bool>("isMDTagger")),
      is_hvv_2d_var_mass_sample_(iConfig.getParameter<bool>("isHVV2DVarMassSample")),
      matcher_(jet_radius_, true) {
  const auto labels = iConfig.getParameter<std::vector<std::string>>("labels");
  for (unsigned int i = 0; i < labels.size(); ++i) {
    const auto label = normalizeLabelName(labels[i]);
    if (!label_to_index_.emplace(label, static_cast<int>(i)).second) {
      throw cms::Exception("Configuration") << "Duplicate fat-jet label '" << label << "'";
    }
  }
  produces<nanoaod::FlatTable>(name_);
}

std::string FatJetMatchingTableProducer::normalizeLabelName(const std::string &label) const {
  const std::string prefix = "label_";
  if (label.rfind(prefix, 0) == 0) {
    return label.substr(prefix.size());
  }
  return label;
}

std::string FatJetMatchingTableProducer::applyHVV2DVarMassLabel(
    const std::string &label,
    const deepntuples::FatJetMatching::FatJetMatchingResult &result) const {
  if (!is_hvv_2d_var_mass_sample_) {
    return label;
  }
  if (result.resParticles.size() <= 2) {
    return label;
  }

  std::string updated = label;
  if (updated.rfind("H_WW", 0) == 0) {
    const float mass_asymm = std::abs(result.resParticles[1]->mass() - result.resParticles[2]->mass()) /
                             (result.resParticles[1]->mass() + result.resParticles[2]->mass());
    updated.replace(updated.find("H_WW"), 4, mass_asymm < 0.1 ? "H_WxWx" : "H_WxWxStar");
  } else if (updated.rfind("H_ZZ", 0) == 0) {
    const float mass_asymm = std::abs(result.resParticles[1]->mass() - result.resParticles[2]->mass()) /
                             (result.resParticles[1]->mass() + result.resParticles[2]->mass());
    updated.replace(updated.find("H_ZZ"), 4, mass_asymm < 0.1 ? "H_ZxZx" : "H_ZxZxStar");
  }
  return updated;
}

int FatJetMatchingTableProducer::labelIndex(const std::string &label) const {
  const auto it = label_to_index_.find(label);
  if (it == label_to_index_.end()) {
    throw cms::Exception("FatJetMatching") << "Unexpected fat-jet label '" << label << "'";
  }
  return it->second;
}

void FatJetMatchingTableProducer::produce(edm::Event &iEvent, const edm::EventSetup &) {
  edm::Handle<edm::View<pat::Jet>> jets;
  edm::Handle<reco::GenParticleCollection> gen_particles;
  iEvent.getByToken(jets_token_, jets);
  iEvent.getByToken(gen_particles_token_, gen_particles);

  std::vector<int> labels;
  labels.reserve(jets->size());
  for (const auto &jet : *jets) {
    matcher_.flavorLabel(&jet, *gen_particles, jet_radius_, is_md_tagger_);
    const auto label = applyHVV2DVarMassLabel(matcher_.getResult().label, matcher_.getResult());
    labels.push_back(labelIndex(label));
  }

  auto table = std::make_unique<nanoaod::FlatTable>(jets->size(), name_, false, true);
  table->addColumn<int>(label_name_,
                        labels,
                        "Generator-level fat-jet truth label index following the matching label order",
                        nanoaod::FlatTable::IntColumn);
  iEvent.put(std::move(table), name_);
}

void FatJetMatchingTableProducer::fillDescriptions(edm::ConfigurationDescriptions &descriptions) {
  edm::ParameterSetDescription desc;
  desc.add<edm::InputTag>("src", edm::InputTag("ak15WithUserData"));
  desc.add<edm::InputTag>("genParticles", edm::InputTag("prunedGenParticles"));
  desc.add<std::string>("name", "AK15Puppi");
  desc.add<std::string>("labelName", "inclParTMDV2_label");
  desc.add<double>("jetRadius", 1.5);
  desc.add<bool>("isMDTagger", true);
  desc.add<bool>("isHVV2DVarMassSample", false);
  desc.add<std::vector<std::string>>("labels", {});
  descriptions.add("fatJetMatchingTableProducer", desc);
}

DEFINE_FWK_MODULE(FatJetMatchingTableProducer);
