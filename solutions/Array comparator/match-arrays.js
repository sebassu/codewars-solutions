const matchArrays = (array1, array2) => {
  const candidateValues = new Set(array1)
  return array2.filter((value) => candidateValues.has(value)).length
}
