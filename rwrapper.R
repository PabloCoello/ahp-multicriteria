set_up <- function(){
  install.packages('reticulate')
  library(reticulate)
  conda_install("r-reticulate", "scipy")
  conda_install("r-reticulate", "pandas")
}


rahp <- function(train, data, pow_value, confidence, cratio_threshold, squema){
  if(!require(reticulate)){set_up()};library(reticulate)
  source_python("saaty.py")
  toret <- ahp(
    train=train,
    data=data,
    pow_value=pow_value,
    confidence=confidence,
    cratio_threshold=cratio_threshold,
    squema=squema
  )
  return(toret)
}