document.addEventListener("DOMContentLoaded", () => {
  const enclaveStatus = document.getElementById("enclave-status");
  const vmStatus = document.getElementById("vm-status");
  const attestation = document.getElementById("attestation");

  document.getElementById("run-workload").addEventListener("click", async () => {
    enclaveStatus.textContent = "Running workload...";
    const res = await fetch("/enclave/compute", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        enclave_name: "demo",
        workload: "keyword_search",
        payload: { documents: ["hello secure world", "secure enclaves"], keyword: "secure" },
      }),
    });
    const data = await res.json();
    enclaveStatus.textContent = `MRENCLAVE: ${data.mrenclave}\nResult: ${JSON.stringify(data.result, null, 2)}`;
  });

  document.getElementById("launch-vm").addEventListener("click", async () => {
    vmStatus.textContent = "Launching VM...";
    const launch = await fetch("/vm/launch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ owner: "dashboard" }),
    });
    const vm = await launch.json();
    vmStatus.textContent = `VM ID: ${vm.vm_id} Measurement: ${vm.measurement}`;

    const attest = await fetch(`/vm/attest?vm_id=${vm.vm_id}`, { method: "POST" });
    const report = await attest.json();
    attestation.textContent = JSON.stringify(report, null, 2);
  });
});
