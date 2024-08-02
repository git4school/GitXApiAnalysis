library(bupaR)
library(xesreadR)

log <- xesreadR::read_xes("out.xes")
plot <- process_map(log, render = F)
export_graph(plot, "out.svg")
