
#___________________________________________________________________________________________________________________________________
#
#             Proyecto: Ajuste estacional de datos ENE
#             Autores: Carolina San Martín
#             Tema: Cálculos - Generacion ajuste para serie de hombres desocupados entre 15 y 24 años
#             Fecha versión: 08/06/2021
#             Tipo de archivo: Cálculos ENE
#
#
#_____________________________________________________________________________________________________________________________________

# Adjuste con seas
X13_dh15 <- seas(dh15,
                 spectrum.savelog = "peaks",
                 spectrum.print = "none",
                 transform.function = "log",
                 transform.print = "none",            
                 regression.variables = c("const","ao2013.aug","ao2013.sep","ao2013.oct","ao2013.dec","ao2014.jan","ao2014.feb","ao2020.mar"),
                 regression.aictest = NULL,
                 regression.savelog = "aictest",
                 outlier.types = c("ao","ls"),
                 arima.model = "(0 1 [3])(1 0 2)", # Parámetros SARIMA
                 identify.diff = 1,
                 identify.sdiff = 1,
                 forecast.maxlead = 12,
                 estimate.savelog = c("aicc","aic","bic","hq","afc"),
                 estimate.print = c("roots","regcmatrix","acm"),
                 check.print = "all",
                 check.savelog = c("lbq","nrm"),
                 x11.seasonalma = "S3X5", #SMA
                 x11.trendma = 9, # MA de Henderson (tendencia)
                 x11.save = c("c17","d8","d9","d10","d11","d12","d13","d16","d18"),
                 x11.savelog = "all")

# Guardar forecast a 12 meses
f <- as.data.frame(series(X13_dh15, "forecast.forecasts"))
names(f)[1] <- "dh15"
names(f)[2] <- "dh15_lower"
names(f)[3] <- "dh15_upper"

#static(X13_dh15, coef = TRUE, test = TRUE)
summary(X13_dh15)

# Gráfico comparativo serie original y ajustada
png(paste0("//buvmfswinp01/ene2/Ajuste estacional/Salidas/Gráficos/", yy,"/", ntm," ",tm,"/Comparación series DH 15-24 ",tm,".png"), width = 700, height = 700)
plot(X13_dh15, 
     main = "DH 15-24 serie original y ajustada", 
     trend = TRUE, 
     xlab = "Periodo", 
     ylab = "Stock ajustado")
legend("topright",c("Serie original","Tendencia","Ajuste estacional"),
       fill=c("black","blue","red"))
dev.off()

# Gráfico de seasonal y seasonal-irregular por mes
png(paste0("//buvmfswinp01/ene2/Ajuste estacional/Salidas/Gráficos/", yy,"/", ntm," ",tm,"/Componente estacional por mes DH 15-24",tm,".png"), width = 700, height = 700)
monthplot(X13_dh15, 
          main = "Componente estacional (ratio SI) para DH 15-24")
legend("topright",c("SI componente","Componente estacional"),
       fill=c("blue","red"))
dev.off() 

# Gráfico de resifuos del regARIMA
png(paste0("//buvmfswinp01/ene2/Ajuste estacional/Salidas/Gráficos/", yy,"/", ntm," ",tm,"/Residuos regARIMA DH 15-24 ",tm,".png"), width = 700, height = 700)
residplot(X13_dh15, 
          main = "Residuos de regArima para DH 15-24",
          xlab = "Periodo")
dev.off()

# Visualizar todos los gráficos disponibles para el modelo en shiny
#view(X13_dh15)

# Salida completa con resultados completos en html para contraste con WinX13
#out(X13_dh25)

# Guardar como df los datos ajustados
seasonal <- as.data.frame(X13_dh15[["data"]])
names(seasonal)[3] <- "dh15_sa"
names(seasonal)[4] <- "dh15_tc"


# Generar tabla con ajuste estacional
SA <- cbind(stock[1], stock[2], seasonal[3])

# Generar tabla para almacenar forecast
for (i in 1:12) {
        if (i==1) {
                mes <- as.data.frame(month(today() - months(2) + months(i)))
                ano <- as.data.frame(year(today() - months(2) + months(i)))
        } else {
        mes <- as.data.frame(rbind(mes,month(today() - months(2) + months(i))))
        ano <- as.data.frame(rbind(ano,year(today() - months(2) + months(i))))
        }
}

forecast <- cbind(ano, mes, f[1], f[2], f[3])
names(forecast)[1] <- "ano"
names(forecast)[2] <- "mes"

# Crear tabla con datos de tendencia
TC <- cbind(ano=stock$ano,mes=stock$mes,seasonal[4])
