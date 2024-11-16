
#************************************************************************************************************************************
#
#             Proyecto: Ajuste estacional de datos ENE
#             Autores: Carolina San Martín
#             Tema: Cálculos - Generacion ajuste para serie de mujeres desocupadas entre 15 y 24 años
#             Fecha versión: 08/06/2021
#             Tipo de archivo: Cálculos ENE
#
#
#************************************************************************************************************************************

# Adjuste con seas
X13_dm15 <- seas(dm15,
                 spectrum.savelog = "peaks",
                 spectrum.print = "none",
                 transform.function = "log",
                 transform.print = "none",            
                 regression.aictest = NULL,
                 regression.savelog = "aictest",
                 outlier.types = c("ao","ls"),
                 #                 automdl.diff = c(1,1),
                 #                 automdl.maxdiff = "1,1",
                 #                 automdl.maxorder = "3,2",
                 #                 automdl.print = c("amd","adt","aft","alb","b5m"),
                 #                 automdl.savelog = "b5m",
                 arima.model = "(0 1 3)(0 0 1)",
                 identify.diff = 1,
                 identify.sdiff = 1,
                 forecast.maxlead = 12,
                 estimate.savelog = c("aicc","aic","bic","hq","afc"),
                 estimate.print = c("roots","regcmatrix","acm"),
                 check.print = "all",
                 check.savelog = c("lbq","nrm"),
                 x11.seasonalma = "S3X5",
                 x11.trendma = 9,
                 x11.save = c("c17","d8","d9","d10","d11","d12","d13","d16","d18"),
                 x11.savelog = "all")

# Guardar forecast a 12 meses
f <- as.data.frame(series(X13_dm15, "forecast.forecasts"))
names(f)[1] <- "dm15"
names(f)[2] <- "dm15_lower"
names(f)[3] <- "dm15_upper"

# Gráfico comparativo serie original y ajustada
png(paste0("//buvmfswinp01/ene2/Ajuste estacional/Salidas/Gráficos/", yy,"/", ntm," ",tm,"/Comparación series DM 15-24 ",tm,".png"), width = 700, height = 700)
plot(X13_dm15, 
     main = "DM 15-24 serie original y ajustada", 
     trend = TRUE, 
     xlab = "Periodo", 
     ylab = "Stock ajustado")
legend("topright",c("Serie original","Tendencia","Ajuste estacional"),
       fill=c("black","blue","red"))
dev.off()

# Gráfico de seasonal y seasonal-irregular por mes
png(paste0("//buvmfswinp01/ene2/Ajuste estacional/Salidas/Gráficos/", yy,"/", ntm," ",tm,"/Componente estacional por mes DM 15-24",tm,".png"), width = 700, height = 700)
monthplot(X13_dm15, 
          main = "Componente estacional (ratio SI) para DM 15-24")
legend("topright",c("SI componente","Componente estacional"),
       fill=c("blue","red"))
dev.off() 

# Gráfico de resifuos del regARIMA
png(paste0("//buvmfswinp01/ene2/Ajuste estacional/Salidas/Gráficos/", yy,"/", ntm," ",tm,"/Residuos regARIMA DM 15-24 ",tm,".png"), width = 700, height = 700)
residplot(X13_dm15, 
          main = "Residuos de regArima para DM 15-24",
          xlab = "Periodo")
dev.off()

# Visualizar todos los gráficos disponibles para el modelo en shiny
#view(X13_dm15)

# Salida completa con resultados completos en html para contraste con WinX13
#out(X13_dm15)

# Guardar como df los datos ajustados
seasonal <- as.data.frame(X13_dm15[["data"]])
names(seasonal)[3] <- "dm15_sa"
names(seasonal)[4] <- "dm15_tc"
SA <- cbind(SA, seasonal[3])

# Actualizar forecast
forecast <- cbind(forecast,f)

# Crear tabla con datos de tendencia
TC <- cbind(TC,seasonal[4])