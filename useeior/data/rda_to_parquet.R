# -------------------------------------
# Script: rda_to_parquet.R
# Author: Sebastian Rowan
# Purpose: Convert useeior .rda data files into parquet format for loading into python version
# Notes:
# -------------------------------------

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
library(useeior)
library(arrow)
library(tools)
library(rio)


files = list.files(path = '.', pattern = "*.rda")
files_lists = files[endsWith(files, "Configuration.rda")]
files = files[!endsWith(files, "Configuration.rda")]

test_files = files[2]

for (file in files){
  new_name = paste0("../../useeio_py/data2/", file_path_sans_ext(file), ".parquet")
  df = rio::import(file)
  rn = .row_names_info(df)
  if (.row_names_info(df) > 0){
    df$index = rownames(df)
  }
  
  write_parquet(df, new_name)
}

