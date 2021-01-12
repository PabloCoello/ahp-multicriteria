est <-
  mlogit(
    as.formula(Choice ~ noChoice + admin_nochoice+ afectado_nochoice +
                 fem_nochoice + ingresos_nochoice + econVulnerability + 
                 socialVulnerability + envVulnerability2 + envVulnerability3 + coste +
                 econVulnerability_ES1+socialVulnerability_ES1+
                 envVulnerability2_ES1+envVulnerability3_ES1+coste_ES1+
                 econVulnerability_ES2+socialVulnerability_ES2+
                 envVulnerability2_ES2+envVulnerability3_ES2+coste_ES2+
                 econVulnerability_ES4+socialVulnerability_ES4+
                 envVulnerability2_ES4+envVulnerability3_ES4+coste_ES4+
                 econVulnerability_ES5+socialVulnerability_ES5+
                 envVulnerability2_ES5+envVulnerability3_ES5+coste_ES5+
                 econVulnerability_ES6+socialVulnerability_ES6+
                 envVulnerability2_ES6+envVulnerability3_ES6+coste_ES6+
                 econVulnerability_ES7+socialVulnerability_ES7+
                 envVulnerability2_ES7+envVulnerability3_ES7+coste_ES7|-1),
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
