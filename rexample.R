library(readxl)
library(jsonlite)

source('rwrapper.R')

data <- read_excel("data/dummy_survey_data.xlsx")
dummy <- read_excel("data/dummy_strat.xlsx")
conf <- fromJSON("./conf/conf.json")
squema <- conf$niveles

res <- rahp(
  train=TRUE,
  data=data,
  pow_value=10,
  confidence=0.95,
  cratio_threshold=0.1,
  squema=squema
)

res$weights
df <- res$set_ahp_weights(dummy)
