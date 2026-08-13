#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"

#include "DataFormats/HepMCCandidate/interface/GenParticle.h"
#include "DataFormats/NanoAOD/interface/FlatTable.h"

#include <algorithm>
#include <cmath>
#include <memory>
#include <vector>

class ZRTo3GluTruthTableProducer : public edm::stream::EDProducer<> {
public:
  explicit ZRTo3GluTruthTableProducer(const edm::ParameterSet &cfg)
      : srcToken_(consumes<reco::GenParticleCollection>(cfg.getParameter<edm::InputTag>("src"))),
        zrPdgId_(cfg.getParameter<int>("zrPdgId")) {
    produces<nanoaod::FlatTable>("GenZR");
    produces<nanoaod::FlatTable>("GenZRProng");
  }

  void produce(edm::Event &event, const edm::EventSetup &) override {
    edm::Handle<reco::GenParticleCollection> particles;
    event.getByToken(srcToken_, particles);

    std::vector<int> zrGenPartIdx, prongGenPartIdx, prongZRIdx, prongSlot;
    for (size_t iz = 0; iz < particles->size(); ++iz) {
      const auto &zr = particles->at(iz);
      if (std::abs(zr.pdgId()) != std::abs(zrPdgId_))
        continue;

      bool hasSamePdgDaughter = false;
      for (size_t id = 0; id < zr.numberOfDaughters(); ++id)
        if (zr.daughter(id) && zr.daughter(id)->pdgId() == zr.pdgId())
          hasSamePdgDaughter = true;
      if (hasSamePdgDaughter)
        continue;

      std::vector<int> gluons;
      for (size_t ig = 0; ig < particles->size(); ++ig) {
        const auto &g = particles->at(ig);
        if (g.pdgId() == 21 && g.numberOfMothers() && g.motherRef(0).key() == iz)
          gluons.push_back(ig);
      }
      if (gluons.size() != 3)
        continue;

      std::sort(gluons.begin(), gluons.end(),
                [&](int a, int b) { return particles->at(a).pt() > particles->at(b).pt(); });
      const int outZRIdx = zrGenPartIdx.size();
      zrGenPartIdx.push_back(iz);
      for (int slot = 0; slot < 3; ++slot) {
        prongGenPartIdx.push_back(gluons[slot]);
        prongZRIdx.push_back(outZRIdx);
        prongSlot.push_back(slot);
      }
    }

    auto zrTable = std::make_unique<nanoaod::FlatTable>(zrGenPartIdx.size(), "GenZR", false);
    zrTable->addColumn<int>("genPartIdx", zrGenPartIdx, "Index of selected ZR in GenPart",
                            nanoaod::FlatTable::IntColumn);
    event.put(std::move(zrTable), "GenZR");

    auto prongTable = std::make_unique<nanoaod::FlatTable>(prongGenPartIdx.size(), "GenZRProng", false);
    prongTable->addColumn<int>("genPartIdx", prongGenPartIdx, "Index of decay gluon in GenPart",
                               nanoaod::FlatTable::IntColumn);
    prongTable->addColumn<int>("zrIdx", prongZRIdx, "Index in GenZR", nanoaod::FlatTable::IntColumn);
    prongTable->addColumn<int>("slot", prongSlot, "Slot ordered by descending gluon pt",
                               nanoaod::FlatTable::IntColumn);
    event.put(std::move(prongTable), "GenZRProng");
  }

  static void fillDescriptions(edm::ConfigurationDescriptions &descriptions) {
    edm::ParameterSetDescription desc;
    desc.add<edm::InputTag>("src", edm::InputTag("finalGenParticles"));
    desc.add<int>("zrPdgId", 32);
    descriptions.addWithDefaultLabel(desc);
  }

private:
  edm::EDGetTokenT<reco::GenParticleCollection> srcToken_;
  int zrPdgId_;
};

DEFINE_FWK_MODULE(ZRTo3GluTruthTableProducer);
