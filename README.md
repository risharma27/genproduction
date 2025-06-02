## Private Production of MC samples

### Production Steps: [EXO gitbook](https://exo-mc-and-i.gitbook.io/exo-mc-and-interpretation/how-to-sample-production-private)
```
gridpack generation >>> LHEGS >>> Premix >> AODSIM >> MINIAODSIM >> NANOAODSIM
```

### Step0: Gridpack generation: [Twiki](https://twiki.cern.ch/twiki/bin/view/CMS/QuickGuideMadGraph5aMCatNLO#Run2_UL_setup)

```
git clone https://github.com/cms-sw/genproductions.git --depth=1
(if you need to use mg 2.4.2 then do mg242legacy, if you need UL with 2.6.5 use mg265UL)
git clone https://github.com/cms-sw/genproductions.git --depth=1 -b mg265UL ##OUR CASE (Run2 UL Setup)
```


#### Preparation of the cards
The process to be generated and the desired cuts and settings are defined in a set of cards:
- ``XXX_proc_card.dat``, where one declares the process to be generated [MANDATORY].  
- ``XXX_run_card.dat``, where one defines particular options on how the generator will run and generate the process, as well as specific kinematic cut values [MANDATORY]  
- ``XXX_customizecards.dat``, where one would set the values of the parameters of the model, such as masses and couplings. In the general use case, this card needs not be modified by the users: the default card contains the agreed-upon values to be used for all processes.  
- ``XXX_extramodels.dat``: if non-SM lagrangians need to be used for the generations, they must be declared here and the related tarballs must be uploaded to the generator web repository.  

Here XXX is a string of your choice. It can be whatever string, but it should be the same string for all the cards.  

Place these cards in the [cards repository on git](https://github.com/cms-sw/genproductions/tree/master/bin/MadGraph5_aMCatNLO/cards).

```
cd genproductions/bin/MadGraph5_aMCatNLO/
./gridpack_generation.sh <name of process card without _proc_card.dat> <folder containing cards relative to current location>
```
e.g.
```
./gridpack_generation.sh VLLD_tau_M100 cards/VLLDoublet/tau/M100
```
### Step1:
