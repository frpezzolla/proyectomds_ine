
#************************************************************************************************************************************
#
#             Proyecto: Ajuste estacional de datos ENE
#             Autores: Carolina San Martín
#             Tema: Cálculos - Generacion ajuste para serie de hombres desocupados de 25 años o más
#             Fecha versión: 08/06/2021
#             Tipo de archivo: Cálculos ENE
#
#
#************************************************************************************************************************************

# Adjuste con seas
X13_dh25 <- seas(dh25,
                 spectrum.savelog = "peaks",
                 spectrum.print = "none",
                 transform.function = "log",
                 transform.print = "none",            
                 regression.variables = c("rp2020.feb-2020.may"),
                 regression.aictest = NULL,
                 regression.savelog = "aictest",
                 outlier.types = c("all"),
                 arima.model = "(0 1 3)(0 1 1)",
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
f <- as.data.frame(series(X13_dh25, "forecast.forecasts"))
names(f)[1] <- "dh25"
names(f)[2] <- "dh25_lower"
names(f)[3] <- "dh25_upper"

summary(X13_dh25)

# Gráfico comparativo serie original y ajustada
png(paste0("//buvmfswinp01/ene2/Ajuste estacional/Salidas/Gráficos/", yy,"/", ntm," ",tm,"/Comparación series DH 25 ",tm,".png"), width = 700, height = 700)
plot(X13_dh25, 
     main = "DH 25 serie original y ajustada", 
     trend = TRUE, 
     xlab = "Periodo", 
     ylab = "Stock ajustado")
legend("topright",c("Serie original","Tendencia","Ajuste estacional"),
       fill=c("black","blue","red"))
dev.off()

# Gráfico de seasonal y seasonal-irregular por mes
png(paste0("//buvmfswinp01/ene2/Ajuste estacional/Salidas/Gráficos/", yy,"/", ntm," ",tm,"/Componente estacional por mes DH 25",tm,".png"), width = 700, height = 700)
monthplot(X13_dh25, 
          main = "Componente estacional (ratio SI) para DH 25")
legend("topright",c("SI componente","Componente estacional"),
       fill=c("blue","red"))
dev.off() 

# Gráfico de resifuos del regARIMA
png(paste0("//buvmfswinp01/ene2/Ajuste estacional/Salidas/Gráficos/", yy,"/", ntm," ",tm,"/Residuos regARIMA DH 25 ",tm,".png"), width = 700, height = 700)
residplot(X13_dh25, 
          main = "Residuos de regArima para DH 25",
          xlab = "Periodo")
dev.off()

# Visualizar todos los gráficos disponibles para el modelo en shiny
#view(X13_dh25)

# Salida completa con resultados completos en html para contraste con WinX13
#out(X13_dh25)

# Guardar como df los datos ajustados
seasonal <- as.data.frame(X13_dh25[["data"]])
names(seasonal)[3] <- "dh25_sa"
names(seasonal)[4] <- "dh25_tc"

# Generar tabla con ajuste estacional
SA <- cbind(SA, seasonal[3])

# Actualizar forecast
forecast <- cbind(forecast,f)

# Crear tabla con datos de tendencia
TC <- cbind(TC,seasonal[4])