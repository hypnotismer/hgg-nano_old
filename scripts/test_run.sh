#!/bin/bash

NEVENT="$1"
NTHREAD="$2"
FILEIN="$3"
FILEOUT="$4"

cmsDriver.py \
    --mc \
    -n "${NEVENT}" \
    --nThreads "${NTHREAD}" \
    --python_filename run-mc-2018.py \
    --eventcontent NANOAODSIM \
    --datatier NANOAODSIM \
    --conditions 106X_upgrade2018_realistic_v16_L1v1 \
    --step NANO \
    --era Run2_2018,run2_nanoAOD_106Xv2 \
    --customise PhysicsTools/NanoTuples/nanoTuples_cff.nanoTuples_customizeMC \
    --filein "${FILEIN}" \
    --fileout "${FILEOUT}" \
    --customise_commands 'process.source.duplicateCheckMode = cms.untracked.string("noDuplicateCheck")' \