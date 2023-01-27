# -------------------------------------
# Script: rda_to_parquet.R
# Author: Sebastian Rowan
# Purpose: Convert useeior .rda data files into parquet format for loading into python version
# Notes:
# -------------------------------------

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
library(arrow)
library(tools)
library(rio)


files = list.files(path = '.', pattern = "*.rda")
files_lists = files[endsWith(files, "Configuration.rda")]
files = files[!endsWith(files, "Configuration.rda")]

for (file in files){
  new_name = paste0("../../useeio_py/data/", file_path_sans_ext(file), ".parquet")
  convert(file, new_name)
}