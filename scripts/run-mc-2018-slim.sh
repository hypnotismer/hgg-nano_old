#!/bin/bash

# Avoid "input: $HOME/.root.mimes, output: $HOME/.root.mimes" error.
# REF: https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideCrabFaq
if [ -z "${HOME}" ]; then
    export HOME="$(pwd)"
fi

if [ $# -lt 3 ]; then
    >&2 echo "usage: $(basename "$0") <nevent> <nthread> <file-in> <file-out>"
    exit 1
fi
NEVENT="$1"
NTHREAD="$2"
FILEIN="$3"
FILEOUT="$4"

if [ -z "${FILEOUT}" ]; then
    FILEOUT="${FILEIN/MiniAODv2/CustomizedNanoAODv9}"
fi
if [ "${FILEIN:0:7}" != "root://" ]; then FILEIN="file:${FILEIN}"; fi
if [ "${FILEOUT:0:7}" != "root://" ]; then FILEOUT="file:${FILEOUT}"; fi

set -ev
voms-proxy-info  # early stop on proxy error

BASEPATH=`pwd`
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc7_amd64_gcc700
[ -r CMSSW_10_6_31 ] || cmsrel CMSSW_10_6_31
cd CMSSW_10_6_31/src
cmsenv

rm -rf PhysicsTools/NanoTuples
git clone https://github.com/hypnotismer/NanoTuples_run2 PhysicsTools/NanoTuples -b dev-ak15tagger-UL-finetune-xggg
PhysicsTools/NanoTuples/scripts/install_onnxruntime.sh
wget https://coli.web.cern.ch/coli/tmp/.231117-195737_ak15_stage2/model.onnx -O $CMSSW_BASE/src/PhysicsTools/NanoTuples/data/InclParticleTransformer-MD/ak15/V02/model.onnx
wget https://zkou.web.cern.ch/tmp/V02_xggg_finetune/model_opset11.onnx -O $CMSSW_BASE/src/PhysicsTools/NanoTuples/data/InclParticleTransformer-MD/ak15/V02_xggg_finetune/model_opset11.onnx
scram b -j$(cat /proc/cpuinfo | grep MHz | wc -l)

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
    --fileout file:out_Nano_1.root \
    --customise_commands 'process.source.duplicateCheckMode = cms.untracked.string("noDuplicateCheck")' \

pwd
ls -lth

mv out_Nano_1.root $BASEPATH
echo "Begin to process step 2"
echo $BASEPATH
ls -lth $BASEPATH

#Second, we produce Ntuple
cd $BASEPATH
echo "The BASEPATH for ntuple production is $BASEPATH"

LOCALInputFile=$BASEPATH/out_Nano_1.root
echo "Input file for NanoAOD-like ntuple production is $LOCALInputFile"

cd $CMSSW_BASE/src
rm -rf PhysicsTools/NanoAODTools
git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git PhysicsTools/NanoAODTools
cd PhysicsTools/NanoAODTools
eval `scram runtime -sh`
scram b -j 16

echo "PhysicsTools/NanoAODTools dir"
pwd
ls -lth

cd python/postprocessing
cp -r $CMSSW_BASE/src/PhysicsTools/NanoTuples/scripts/analysis  .
echo "Successfully get analysis files"

cd $CMSSW_BASE/src
scram b -j 16

cd $CMSSW_BASE/src/PhysicsTools/NanoAODTools/python/postprocessing/analysis
echo "analysis dir"
pwd
ls -lth

echo python run_condor.py -i $LOCALInputFile 
python run_condor.py -i $LOCALInputFile -o $BASEPATH --year 2018 -m True

pwd
ls -lth

WORKPATH=`pwd`
path=$WORKPATH/tree.root
xrdcp --silent -p -f ${path} ${FILEOUT}