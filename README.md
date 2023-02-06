# useeio_py

`useeio_py` is a Python translation of the USEPA's [useeior](https://github.com/USEPA/useeior) R package for building and using [USEEIO models](https://www.epa.gov/land-research/us-environmentally-extended-input-output-useeio-models).

I started this project to incorporate some of the functionality of the original R package into existing Python code for my dissertation research. This is a personal hobby project and I am not affiliated with the EPA. This package is not being developed in coordination with anyone from the EPA, nor has any of this work gone through peer-review.

If this package is ever completed, and you use it in any peer-reviewed scientific publication, please include a citation for the original peer-reviewed `useeior` publication included below. While I would certainly appreciate an acknowledgement for the Python translation, all credit for the research and development of the modelling framework goes to the team at the EPA.

`useeior` citation:
```
@article{li_useeior_2022,
  title   = {useeior: {An} {Open-Source} {R} {Package} for {Building} and {Using} {US} {Environmentally-Extended} {Input-Output} {Models}},
  journal = {Applied Sciences},
  author  = {{Li, Mo} and {Ingwersen, Wesley} and {Young, Ben} and {Vendries, Jorge} and {Birney, Catherine}},
  year    = {2022},
  pages   = {4469},
  number  = {9},
  volume  = {12},
  doi     = {10.3390/app12094469}
}
```
or
```
Li, M., Ingwersen, W.W., Young, B., Vendries, J. and Birney, C., 2022. useeior: An Open-Source R Package for Building and Using US Environmentally-Extended Input–Output Models. Applied Sciences, 12(9), p.4469.
```
## Installation

Version 0 not complete yet.

## Usage

### Build Model

View all models with existing config files that can be built using useeio_py

```python
from useeio_py import configuration_functions

configuration_functions.see_available_models()
```

Build a model that is available in useeior (e.g. the [USEEIOv2.0.1-411](useeio_py/inst/extdata/modelspecs/USEEIOv2.0.1-411.yml) model)

```python
from useeio_py.useeio_model import USEEIOModel

model = USEEIOModel('USEEIOv2.0.1-411')
```

This generates a complete USEEIO model with components described in the [Model](useeio_py/format_specs/Model.md#model) table.

### Adjust Price Year and Type of Model Results

Adjust model results (e.g. `N` matrix) to user-specified price year (e.g. `2018`) and type (producer's or purchaser's).

```python
from useeio_py import adjust_price

N_adj = adjust_price.adjust_result_matrix_price(model, "N", currency_year = 2018, purchaser_price = True)
```

### Calculate Model LCI and LCIA

Calculate model life cycle inventory (LCI) and life cycle impact assessment (LCIA) results with a user-specified [calculation perspective](useeio_py/format_specs/Calculation.md#calculation-perspectives), [demand vector](format_specs/Model.md#demandvectors) (from `DemandVectors` in the model object, which includes four [default vectors](useeio_py/format_specs/ModelSpecification.md#demand-vector-specifications), or a user-provided vector) and a model [direct requirements matrix](useeio_py/format_specs/Model.md#a).

```python
from useeio_py import calculation_functions

result = calculation_functions.calculate_EEIO_model(model, perspective = "DIRECT", demand = "CompleteProduction", use_domestic_requirements = False)
```

This returns a [Calculation Result](useeio_py/format_specs/Calculation.md#calculation-result). 

### Write Model to File

Write selected model matrices, demand vectors, and metadata as one `.xlsx` file to a given output folder.
```python
from useeio_py import write_model

write_model_to_xlsx(model, outputfolder)
```

Write model matrices as `.csv` files to a given output folder.
```python
from useeio_py import write_model

write_model_matrices(model, to_format = "csv", output_folder = "/path/to/output_folder")
```

<!---
### Validate Model

Complete model validation checks can be found in [ValidateModel.Rmd](inst/doc/ValidateModel.Rmd).
Knit [ValidateModel_render.Rmd](inst/doc/ValidateModel_render.Rmd) to perform all validation checks on selected models (specified under the [YAML header](inst/doc/ValidateModel_render.Rmd#L5)).
This will generate an `.html` and a `.md` file containing validation results for each model. See example output in  [inst/doc/output/](inst/doc/output). 

#### Examples

Validate that flow totals by commodity `E_c` can be recalculated (within 1%) using the model satellite matrix `B`, market shares matrix `V_n`, total requirements matrix `L`, and demand vector `y` for US production.

```r
> modelval <- compareEandLCIResult(model, tolerance = 0.01)
> print(paste("Number of flow totals by commodity passing:", modelval$N_Pass))
[1] "Number of flow totals by commodity passing: 1118742"
> print(paste("Number of flow totals by commodity failing:", modelval$N_Fail))
[1] "Number of flow totals by commodity failing: 0"
```

Validate that commodity output can be recalculated (within 1%) with the model total requirements matrix `L` and demand vector `y` for US production.

```r
> econval <- compareOutputandLeontiefXDemand(model, tolerance = 0.01)
> print(paste("Number of sectors passing:",econval$N_Pass))
[1] "Number of sectors passing: 409"
> print(paste("Number of sectors failing:",econval$N_Fail))
[1] "Number of sectors failing: 2"
> print(paste("Sectors failing:", paste(econval$Failure$rownames, collapse = ", ")))
[1] "Sectors failing: S00402/US, S00300/US"
```
Note: `S00402/US - Used and secondhand goods` and `S00300/US - Noncomparable imports` are two commodities that are not produced by any industry in the US, therefore their commodity output naturally cannot be recalculated with the model total requirements matrix `L` and demand vector `y` for US production. Results for these sectors are not recommended for use.

### Visualize Model Results

#### Examples

Rank sectors based a composite score of selected total impacts (LCIA_d or LCIA_f) associated with total US demand (US production or consumption vector).
Comparing rankings may also be used as another form of model validation that incorporates the demand vectors and the indicators as well as the model result matrices.

```r
# Calculate model LCIA_d and LCIA_f
result <- c(calculateEEIOModel(model, perspective = 'DIRECT', demand = "Production"),
            calculateEEIOModel(model, perspective = 'FINAL', demand = "Consumption"))
colnames(result$LCIA_d) <- model$Indicators$meta[match(colnames(result$LCIA_d),
                                                       model$Indicators$meta$Name),
                                                 "Code"]
colnames(result$LCIA_f) <- colnames(result$LCIA_d)
# Define indicators
indicators <- c("ACID", "CCDD", "CMSW", "CRHW", "ENRG", "ETOX", "EUTR", "GHG",
                "HRSP", "HTOX", "LAND", "MNRL", "OZON", "SMOG", "WATR")
# Create figure on the left
heatmapSectorRanking(model,
                     matrix = result$LCIA_d,
                     indicators,
                     sector_to_remove = "",
                     N_sector = 20,
                     x_title = "LCIA_d (DIRECT perspective) & US production demand")
# Create figure on the right
heatmapSectorRanking(model,
                     matrix = result$LCIA_f,
                     indicators,
                     sector_to_remove = "",
                     N_sector = 20,
                     x_title = "LCIA_f (FINAL perspective) & US consumption demand")
```

![](inst/img/ranking_direct_prod_final_cons_v2.0.1.png)

More visualization examples are available in [Example.Rmd](inst/doc/Example.Rmd).

### Analyze Flow and Sector Contribution to Impact

#### Examples

Analyze `flow` contribution to total (direct+indirect) `Acidification Potential` in the `Electricity` sector (`221100/US`), showing top 5 contributors below.

```r
> ACID_elec <- calculateFlowContributiontoImpact(model, "221100/US", "Acidification Potential")
> ACID_elec$contribution <- scales::percent(ACID_elec$contribution, accuracy = 0.1)
> head(subset(ACID_elec, TRUE, select = "contribution"), 5)
                                    contribution
"Sulfur dioxide/emission/air/kg"           57.4%
"Nitrogen dioxide/emission/air/kg"         39.2%
"Ammonia/emission/air/kg"                   2.3%
"Sulfuric acid/emission/air/kg"             0.7%
"Hydrofluoric acid/emission/air/kg"         0.2%
```

Analyze `sector` contribution to total (direct+indirect) `Human Health - Respiratory Effects` in the `Flours and malts` sector (`311210/US`), showing top 5 contributors below.

```r
> HHRP_flour <- calculateSectorContributiontoImpact(model, "311210/US", "Human Health - Respiratory Effects")
> HHRP_flour$contribution <- scales::percent(HHRP_flour$contribution, accuracy = 0.1)
> head(subset(HHRP_flour, TRUE, select = "contribution"), 5)
                                                                        contribution
"1111B0/US - Fresh wheat, corn, rice, and other grains"                        90.7%
"311210/US - Flours and malts"                                                  1.5%
"115000/US - Agriculture and forestry support"                                  0.9%
"2123A0/US - Sand, gravel, clay, phosphate, other nonmetallic minerals"         0.8%
"1111A0/US - Fresh soybeans, canola, flaxseeds, and other oilseeds"             0.8%
```

More analysis examples are available in [Example.Rmd](inst/doc/Example.Rmd).

### Compare Model Results

Comparison betwen two models can be found in [CompareModel.Rmd](inst/doc/CompareModels.Rmd).
Knit [CompareModel_render.Rmd](inst/doc/CompareModels_render.Rmd) to perform comparison on selected models (specified under the [YAML header](inst/doc/CompareModels_render.Rmd#L5)).
This will return an `.html` and a `.md` file containing comparison results for each model specified in the header. An example can be found [inst/doc/output/](inst/doc/output)

Currently, it only compares flow totals between two models. More comparisons will be added in the future.

### Additional Information

A complete list of available functions for calculating, validating, exporting and visualizing model can be found [here](https://github.com/USEPA/useeior/wiki/Using-useeior#calculate-validate-export-visualize-model) in the Wiki.

## Disclaimer

The United States Environmental Protection Agency (EPA) GitHub project code is provided on an "as is" basis and the user assumes responsibility for its use.  EPA has relinquished control of the information and no longer has responsibility to protect the integrity , confidentiality, or availability of the information.  Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise, does not constitute or imply their endorsement, recommendation or favoring by EPA.  The EPA seal and logo shall not be used in any manner to imply endorsement of any commercial product or activity by EPA or the United States Government.
-->
