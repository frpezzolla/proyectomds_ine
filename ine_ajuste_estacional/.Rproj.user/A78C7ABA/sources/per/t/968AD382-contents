
#************************************************************************************************************************************
#
#             Proyecto: Ajuste estacional de datos ENE
#             Autores: Carolina San Martín
#             Tema: Cálculos - Generacion ajuste para serie de hombres ocupados entre 15 y 24 años
#             Fecha versión: 08/06/2021
#             Tipo de archivo: Cálculos ENE
#
#
#************************************************************************************************************************************

# Adjuste con seas
X13_oh15 <- seas(oh15,
                 spectrum.savelog = "peaks",
                 spectrum.print = "none",
                 transform.function = "log",
                 transform.print = "none",            
                 regression.variables = c("rp2020.feb-2020.may","ao2020.apr","ao2020.sep","ls2020.oct"),
                 regression.aictest = NULL,
                 regression.savelog = "aictest",
                 outlier = NULL,
                 #                 outlier.types = c("all"),
                 #                 automdl.diff = c(0,1),
                 #                 automdl.maxdiff = "1,1",
                 #                 automdl.maxorder = "3,2",
                 #                 automdl.print = c("amd","adt","aft","alb","b5m"),
                 #                 automdl.savelog = "b5m", 
                 arima.model = "([3 5] 1 0)(1 1 0)",
                 identify.diff = 1,
                 identify.sdiff = 1,
                 forecast.maxlead = 12,
                 estimate.savelog = c("aicc","aic","bic","hq","afc"),
                 estimate.print = c("roots","regcmatrix","acm"),
                 check.print = "all",
                 check.savelog = c("lbq","nrm"),
                 x11.seasonalma = "S3X5",
                 x11.trendma = 13,
                 x11.save = c("c17","d8","d9","d10","d11","d12","d13","d16","d18"),
                 x11.savelog = "all")

# Guardar forecast a 12 meses
f <- series(X13_oh15, "forecast.forecasts")
f <- as.data.frame(series(X13_oh15, "forecast.forecasts"))
names(f)[1] <- "oh15"
names(f)[2] <- "oh15_lower"
names(f)[3] <- "oh15_upper"

#static(X13_oh15, coef = TRUE, test = TRUE)
summary(X13_oh15)

# Gráfico comparativo serie original y ajustada
png(paste0("//buvmfswinp01/ene2/Ajuste estacional/Salidas/Gráficos/", yy,"/", ntm," ",tm,"/Comparación series OH 15-24 ",tm,".png"), width = 700, height = 700)
        plot(X13_oh15, 
             main = "OH 15-24 serie original y ajustada", 
             trend = TRUE, 
             xlab = "Periodo", 
             ylab = "Stock ajustado")
             legend("topright",c("Serie original","Tendencia","Ajuste estacional"),
                fill=c("black","blue","red"))
dev.off()

# Gráfico de seasonal y seasonal-irregular por mes
png(paste0("//buvmfswinp01/ene2/Ajuste estacional/Salidas/Gráficos/", yy,"/", ntm," ",tm,"/Componente estacional por mes OH 15-24",tm,".png"), width = 700, height = 700)
        monthplot(X13_oh15, 
                  main = "Componente estacional (ratio SI) para OH 15-24")
                  legend("topright",c("SI componente","Componente estacional"),
                         fill=c("blue","red"))
dev.off() 

# Gráfico de resifuos del regARIMA
png(paste0("//buvmfswinp01/ene2/Ajuste estacional/Salidas/Gráficos/", yy,"/", ntm," ",tm,"/Residuos regARIMA OH 15-24 ",tm,".png"), width = 700, height = 700)
        residplot(X13_oh15, 
                  main = "Residuos de regArima para OH 15-24",
                  xlab = "Periodo")
dev.off()

# Visualizar todos los gráficos disponibles para el modelo en shiny
#view(X13_oh15)

# Salida completa con resultados completos en html para contraste con WinX13
#out(X13_oh15)

# Guardar como df los datos ajustados
seasonal <- as.data.frame(X13_oh15[["data"]])
names(seasonal)[3] <- "oh15_sa"
names(seasonal)[4] <- "oh15_tc"

# Generar tabla con ajuste estacional
SA <- cbind(SA, seasonal[3])

# Actualizar forecast
forecast <- cbind(forecast,f)

# Crear tabla con datos de tendencia
TC <- cbind(TC,seasonal[4])
