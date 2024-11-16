
#' @title 
#' Proyecto: Ajuste estacional tasa de desocupación ENE
#' 
#' @description 
#' Actualiza las tablas de estimaciones históricas con el panel de trimestre t y t-1
#' 
#' @details 
#' Este código permite actualizar las tablas históricas de transiciones de estados laborales 
#' /ocupación, desocupación, fuera de la FT y sus razones de inactividad/
#' considerando el trimestre t de producción con su trimestre calendario anterior.
#' Fecha versión: 08/06/2021
#' 
#' @docType
#' Estimaciones
#' 
#' @author 
#' Carolina San Martín
#' Maintainer: Carolina San Martín 


# Leer base de publicación
load(paste0("//buvmfswinp01/ene2/Boletines/Bases/",yy,"-",mm,".RData"))

# Importar histórico DEEC/stock
load("../Insumos/Históricos/Histórico.RData")

# Contar desocupados por sexo
dh15 <- base %>% filter(cse_especifico %in% 8:9 & edad %in% 15:24 & sexo==1) %>%
        group_by(mes_central) %>% summarise(dh15=sum(fact_cal)) %>% select(-mes_central)
dm15 <- base %>% filter(cse_especifico %in% 8:9 & edad %in% 15:24 & sexo==2) %>%
        group_by(mes_central) %>% summarise(dm15=sum(fact_cal)) %>% select(-mes_central)
dh25 <- base %>% filter(cse_especifico %in% 8:9 & edad >= 25 & sexo==1) %>%
        group_by(mes_central) %>% summarise(dh25=sum(fact_cal)) %>% select(-mes_central)
dm25 <- base %>% filter(cse_especifico %in% 8:9 & edad >= 25 & sexo==2) %>%
        group_by(mes_central) %>% summarise(dm25=sum(fact_cal)) %>% select(-mes_central)

# Contar ocupados por sexo
oh15 <- base %>% filter(cse_especifico %in% 1:7 & edad %in% 15:24 & sexo==1) %>%
        group_by(mes_central) %>% summarise(oh15=sum(fact_cal)) %>% select(-mes_central)
om15 <- base %>% filter(cse_especifico %in% 1:7 & edad %in% 15:24 & sexo==2) %>%
        group_by(mes_central) %>% summarise(om15=sum(fact_cal)) %>% select(-mes_central)
oh25 <- base %>% filter(cse_especifico %in% 1:7 & edad >= 25 & sexo==1) %>%
        group_by(mes_central) %>% summarise(oh25=sum(fact_cal)) %>% select(-mes_central)
om25 <- base %>% filter(cse_especifico %in% 1:7 & edad >= 25 & sexo==2) %>%
        group_by(mes_central) %>% summarise(om25=sum(fact_cal)) %>% select(-mes_central)

# Generar dataframe con la fila a agregar en tabla histórica
m1 <- cbind(dh15, dm15, dh25, dm25, oh15, om15, oh25, om25) 
m1 <- cbind(m1, desocupados = rowSums(m1[,1:4]), 
            ocupados = rowSums(m1[,5:8]), dh = rowSums(m1[,c("dh15","dh25")]),
            dm = rowSums(m1[,c("dm15","dm25")]), oh = rowSums(m1[,c("oh15","oh25")]),
            om = rowSums(m1[,c("om15","om25")]))
m1 <- cbind(m1, ft_h = rowSums(m1[,c("dh","oh")]), ft_m = rowSums(m1[,c("dm","om")]), 
            ft = rowSums(m1[,c("desocupados","ocupados")]))
m1 <- cbind(m1, td_h = ((m1$dh/m1$ft_h)*100), td_m = ((m1$dm/m1$ft_m)*100), td = ((m1$desocupados/m1$ft)*100))


# Cargar columnas con fecha asociadas a submuestra
m1%<>%mutate(ano=yy, mes=mm)

# Actualiza historico con mes t
m1 <- m1[,c(21,22,1:20)]

#stock <-rbind(stock, m1)
#stock<-stock[1:134,]

if (ifelse(mm==1, stock$ano[nrow(stock)]==yy-1 & stock$mes[nrow(stock)]==mm+11, stock$ano[nrow(stock)]==yy & stock$mes[nrow(stock)]==mm-1)) { 
        stock <-rbind(stock, m1)
} else {
        stock<-stock
}

# Guardar rdata histórico actualizado
save(stock, file= "../Insumos/Históricos/Histórico.RData")


