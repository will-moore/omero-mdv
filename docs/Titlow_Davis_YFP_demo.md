
Titlow Davis demo data
======================

The MDV viewer at https://mdv.molbiol.ox.ac.uk/projects/mdv_project/7012
shows data from publication: [Titlow etal: Systematic analysis of YFP traps reveals common mRNA/protein discordance in neural tissues](https://rupress.org/jcb/article/222/6/e202205129/214092/Systematic-analysis-of-YFP-traps-reveals-common).

The following steps describe how to download the data, import into OMERO and view in OMERO.MDV.

 - Download the images (1.7 GB) from https://zenodo.org/record/7308444/files/Figures.zip?download=1 and unzip.
 - Unzip each of the 7 sub-directories.
 - Download the metadata csv from https://zenodo.org/record/7308444/files/Davis%20lab%20200%20YFP%20trap%20expression.csv?download=1
 - Import all the images from the `Figures` directory above creating a Dataset corresponding to each subdirectory within a Project e.g named `Davis_Titlow_YFP_distribution`. You can do this manually using OMERO.insight or with the following commands:

```
omero login
cd Figures
project=$(omero obj new Project name='Titlow_Davis_YFP_distribution')

for d in $(ls -d */ | sed 's/\/$//'); do
  dataset=$(omero obj new Dataset name=$d)
  omero obj new ProjectDatasetLink parent=$project child=$dataset
  omero import -d $dataset $d
done
```

 - You need to update the `KeyVal_from_csv.py` script as described at https://github.com/ome/omero-scripts/issues/213 and update this onto your OMERO server (this requires Admin permissions and can be done under the `scripts` menu in the webclient). Then select all 6 Datasets in the webclient and choose to run the script, choosing the CSV file as input. When the script completes you should see a message like `Added kv pairs to 1158/1173 files. 7008 image names not found.` This is expected as the CSV has lots of rows that do not have images.
 - Now you can select the Project, right-click and `Open with > MDV`
