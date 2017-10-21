typedef pair<int, int> pr;

void VALE(bE, sE, bZ, sZ){
  if((bZ.first - sE.first) * min(sE.second, bZ.second) > 15){
    int units = min(sE.second, bZ.second);
    buy(E, units);
    convert(E, sell, units)
    sell(Z, units);
  }
  if((bE.first - sZ.first) * min(sZ.second, bE.second) > 15){
    int units = min(sZ.second, bE.second);
    buy(Z, units);
    convert(E, buy, units)
    sell(E, units);
  }
}
