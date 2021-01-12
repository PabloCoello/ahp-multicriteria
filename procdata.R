format_multi_df <- function(sondaxe, multi_conf, columns) {
  #' Format raw df from google forms.
  #'
  #' Note that the questions are hardcoded into the function.
  
  criterios <-
    sondaxe[,columns[grep(c('A'), columns)]] # Get first part of the question
  grados <-
    sondaxe[,columns[grep(c('B'), columns)]]# Get second part of the question
  
  # Rename both parts with the criteria of the question (from conf)
  for (col in 1:length(colnames(criterios))) {
    colnames(criterios)[col] <- multi_conf[['pares']][as.character(col)]
    colnames(grados)[col] <- multi_conf[['pares']][as.character(col)]
  }
  
  # Remove na rows from criterios in criterios and grados
  criterios.na <- complete.cases(criterios)
  criterios <- criterios[criterios.na, ]
  grados <- grados[criterios.na, ]
  
  # Remove na rows from grados in criterios and grados
  grados.na <- complete.cases(grados)
  criterios <- criterios[grados.na, ]
  grados <- grados[grados.na, ]
  
  return(list(criterios, grados))
}

setwd(system("pwd", intern = T))
multi_conf <- fromJSON(file = './conf/multicriteria_conf.json')

# Preprocess data:
df <- read.csv2(multi_conf[['path_to_file']])
list <- format_multi_df(df, multi_conf)

write.csv2(list[[1]], './data/criterios.csv')
write.csv2(list[[2]], './data/grados.csv')
