import os
import json

with open("modeldict.json") as f:
    modeldict = json.load(f)

isospin_map = {"singlet": "0", "doublet": "-0.5"}

with open("templates/proc_card_singlet.dat") as f: proc_singlet_template = f.read()
with open("templates/proc_card_doublet.dat") as f: proc_doublet_template = f.read()
with open("templates/extramodels.dat") as f:       extramodels_template = f.read()
with open("templates/customizecards.dat") as f:    customize_template = f.read()
with open("templates/run_card.dat") as f:          run_card_content = f.read()

count = 0
for idx, (tag, info) in enumerate(modeldict.items()):
    model = info["model"]
    tarfile = info["tarfile"]
    coupling = info["coupling"]
    masses = info["masses"]
    isospin = isospin_map[info["type"]]
    model_archive = f"{model}.tar.gz"

    # Define decay leptons based on coupling
    if   coupling == "mu":  decay_lepton = "mu+ mu- vm vm~"
    elif coupling == "e":   decay_lepton = "e+ e- ve ve~"
    elif coupling == "tau": decay_lepton = "ta+ ta- vt vt~"
    else : decay_lepton = "e+ e- mu+ mu- ta+ ta- ve ve~ vm vm~ vt vt~"

    for mass in masses:
        count += 1
        
        prefix = f"{tag}_M{mass}"
        outdir = os.path.join("cards", prefix)
        os.makedirs(outdir, exist_ok=True)

        print(f"{count}. Processing cards for: {prefix} .. ", end = '\t')

        # 1) proc_card
        if info["type"] == "singlet":
            proc = proc_singlet_template.format(model=model, decay_lepton=decay_lepton, output_name=prefix)
        else:  # doublet
            proc = proc_doublet_template.format(model=model, decay_lepton=decay_lepton, output_name=prefix)
        with open(os.path.join(outdir, f"{prefix}_proc_card.dat"), "w") as f: f.write(proc)

        # 2) customizecards
        customize = customize_template.format(mass=mass,isospin=isospin)
        with open(os.path.join(outdir, f"{prefix}_customizecards.dat"), "w") as f: f.write(customize)

        # 3) extramodels
        extramodels = extramodels_template.format(model_archive=tarfile)
        with open(os.path.join(outdir, f"{prefix}_extramodels.dat"), "w") as f: f.write(extramodels)

        # run_card (copied as-is)
        with open(os.path.join(outdir, f"{prefix}_run_card.dat"), "w") as f: f.write(run_card_content)

        print(f"Done: \033[93m{outdir}\033[0m")
