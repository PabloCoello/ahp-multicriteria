df <- data

df$econCoste <- df$econVulnerability*df$coste
df$socialCoste <- df$socialVulnerability*df$coste
df$env2Coste <- df$envVulnerability2*df$coste
df$env3Coste <- df$envVulnerability3*df$coste
df$noChoiceCoste <- df$noChoice*df$coste

#df$coste <- df$coste*1000
#df$socialVulnerability <- df$socialVulnerability*1000
#df$econVulnerability <- df$econVulnerability*1000
#df$coste <- df$coste*1000

df$P1_7 <- (((df$P1_7-1) * -1)+1)
df$afectado_nochoice <- df$noChoice * df$P1_7

df$P1_5 <- (((df$P1_5-1) * -1)+1)
df$admin_nochoice <- df$noChoice * df$P1_5

df$P5_1 <- df$P5_1-1
df$fem_nochoice <- df$noChoice * df$P5_1
df <- df[which(df$P5_1!=2),]

df$ingresos_nochoice <- df$noChoice * df$P5_6

variables <- c('econVulnerability','socialVulnerability','envVulnerability2',
               'envVulnerability3','coste')
codigos <- read_excel("Results/Results/codigos_ccaa.xlsx")
for(region in codigos$ccaa){
  print(region)
  cod <- codigos[which(codigos$ccaa == region),"codigo"]
  for(var in variables){
    df[,paste(var, cod, sep='_')] <- 0
    for(row in 1:nrow(df)){
      if(df[row, "P1_CCAA"]==cod){
        df[row, paste(var, cod, sep='_')] <- df[row, var]
      }
    }
  }
}

df$nut <- 'No region'
for(row in 1:nrow(df)){
  df[row, 'nut'] <- codigos[which(codigos$codigo == df[row, "P1_CCAA"]),"NUT"]
}

for(nut in unique(df$nut)){
  print(nut)
  for(var in variables){
    df[,paste(var, nut, sep='_')] <- 0
    for(row in 1:nrow(df)){
      if(df[row, "nut"]==nut){
        df[row, paste(var, nut, sep='_')] <- df[row, var]
      }
    }
  }
}


#df <- df[which(df$P1_CCAA==17),]
df[which(df$P1_CCAA==1),'Andalucía_coste']


est <-
  mlogit(
    as.formula(Choice ~ noChoice + admin_nochoice+ afectado_nochoice +
      fem_nochoice + ingresos_nochoice + econVulnerability + 
      socialVulnerability + envVulnerability2 + envVulnerability3 + coste +
      econVulnerability_1+socialVulnerability_1+
      envVulnerability2_1+envVulnerability3_1+coste_1+
      econVulnerability_2+socialVulnerability_2+
      envVulnerability2_2+envVulnerability3_2+coste_2+
      econVulnerability_3+socialVulnerability_3+
      envVulnerability2_3+envVulnerability3_3+coste_3+
      econVulnerability_4+socialVulnerability_4+
      envVulnerability2_4+envVulnerability3_4+coste_4+
      econVulnerability_5+socialVulnerability_5+
      envVulnerability2_5+envVulnerability3_5+coste_5+
      econVulnerability_6+socialVulnerability_6+
      envVulnerability2_6+envVulnerability3_6+coste_6+
      econVulnerability_7+socialVulnerability_7+
      envVulnerability2_7+envVulnerability3_7+coste_7+
      econVulnerability_8+socialVulnerability_8+
      envVulnerability2_8+envVulnerability3_8+coste_8+
      econVulnerability_9+socialVulnerability_9+
      envVulnerability2_9+envVulnerability3_9+coste_9+
      econVulnerability_10+socialVulnerability_10+
      envVulnerability2_10+envVulnerability3_10+coste_10+
      econVulnerability_11+socialVulnerability_11+
      envVulnerability2_11+envVulnerability3_11+coste_11+
      econVulnerability_12+socialVulnerability_12+
      envVulnerability2_12+envVulnerability3_12+coste_12+
      econVulnerability_13+socialVulnerability_13+
      envVulnerability2_13+envVulnerability3_13+coste_13+
      econVulnerability_14+socialVulnerability_14+
      envVulnerability2_14+envVulnerability3_14+coste_14+
      econVulnerability_15+socialVulnerability_15+
      envVulnerability2_15+envVulnerability3_15+coste_15+
      econVulnerability_16+socialVulnerability_16+
      envVulnerability2_16+envVulnerability3_16+coste_16|-1),
    df,
    rpar = c(
      econVulnerability = 'n',
      socialVulnerability = 'n',
      envVulnerability2 = 'n',
      envVulnerability3 = 'n',
      coste = 'n'
    ),
    R = 1000,
    halton = NA,
    panel = TRUE
  )
summary(est)

write.csv2(df, 'panel.csv')

