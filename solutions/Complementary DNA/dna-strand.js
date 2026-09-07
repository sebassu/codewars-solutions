const basePairs = {
  A: "T",
  T: "A",
  G: "C",
  C: "G",
};

function DNAStrand(dna) {
  return dna.replace(/./g, (base) => basePairs[base]);
}
