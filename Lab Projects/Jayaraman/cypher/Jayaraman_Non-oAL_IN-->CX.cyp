// See this folder in google drive to see the results organized 


// A1. True CX Direct Connectivity Matrix

  // Connectivity matrix query - this is the query, but it does not tell you if b is in the "true CX" cell type. Use python file "TrueCXDirect" 
  WITH [603785283,634759240,663432544,663787020,664814903,850717220,1639234609,1639243580,1727979406,1755556097,1858901026,1881401277,
  1943811736,1943812176,1944502935,1975187675,1975878958,2069648663,5813040515,5813056072,5813063239]AS TARGETS 
  MATCH (a:Neuron)-[w:ConnectsTo]->(b:Neuron)
  WHERE a.bodyId IN TARGETS AND b.`CX`
  RETURN a.bodyId, a.type, w.weight, b.bodyId, b.type
  
  
// A2. Direct True CX Abbreviated
  
  // Distinct Non-oAL_INs 
  WITH [603785283,634759240,663432544,663787020,664814903,850717220,1639234609,1639243580,1727979406,1755556097,1858901026,1881401277,
  1943811736,1943812176,1944502935,1975187675,1975878958,2069648663,5813040515,5813056072,5813063239]AS TARGETS 
  MATCH (a:Neuron)-[w:ConnectsTo]->(b:Neuron)
  WHERE a.bodyId IN TARGETS AND b.`CX`
  RETURN DISTINCT a.bodyId, COUNT(b), SUM(w.weight), (a.pre+a.post), 
