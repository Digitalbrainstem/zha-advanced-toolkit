class ZhaAdvancedToolkitPanel extends HTMLElement {
  set hass(hass) {
    this._hass = hass;
    if (!this._loaded) {
      this._loaded = true;
      this.loadDevices();
    }
  }

  connectedCallback() {
    this.renderShell();
  }

  renderShell() {
    this.innerHTML = `
      <style>
        :host { display: block; padding: 24px; color: var(--primary-text-color); }
        .toolbar { display: flex; gap: 12px; align-items: center; margin-bottom: 20px; }
        select, input { background: var(--card-background-color); color: var(--primary-text-color); border: 1px solid var(--divider-color); border-radius: 4px; padding: 8px; }
        button { background: var(--primary-color); color: var(--text-primary-color); border: 0; border-radius: 4px; padding: 8px 12px; cursor: pointer; }
        button.secondary { background: var(--secondary-background-color); color: var(--primary-text-color); border: 1px solid var(--divider-color); }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap: 16px; }
        .card { background: var(--ha-card-background, var(--card-background-color)); border-radius: 12px; box-shadow: var(--ha-card-box-shadow); padding: 16px; border: 1px solid var(--divider-color); }
        .row { display: grid; grid-template-columns: 1fr auto auto; gap: 8px; align-items: center; padding: 8px 0; border-top: 1px solid var(--divider-color); }
        .row:first-of-type { border-top: 0; }
        .raw-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 8px; margin: 8px 0; }
        .raw-grid label { display: grid; gap: 4px; font-size: 12px; color: var(--secondary-text-color); }
        .raw-list { max-height: 280px; overflow: auto; margin-top: 12px; font-size: 12px; color: var(--secondary-text-color); }
        .name { font-weight: 500; }
        .meta { color: var(--secondary-text-color); font-size: 12px; }
        .status { margin: 8px 0 16px; color: var(--secondary-text-color); }
        h1 { margin-top: 0; }
        h2 { margin: 0 0 8px; }
      </style>
      <h1>ZHA Advanced Toolkit</h1>
      <div class="toolbar">
        <label>Device</label>
        <select id="device"></select>
        <button class="secondary" id="refresh">Refresh</button>
      </div>
      <div class="status" id="status">Loading...</div>
      <div class="grid" id="content"></div>
    `;
    this.querySelector("#refresh")?.addEventListener("click", () => this.loadDevices());
    this.querySelector("#device")?.addEventListener("change", () => this.renderDevice());
  }

  async loadDevices() {
    if (!this._hass) return;
    this.setStatus("Loading devices...");
    try {
      this._devices = await this._hass.callWS({ type: "zha_advanced_toolkit/devices" });
      const selectedIeee = new URLSearchParams(window.location.search).get("ieee");
      const selector = this.querySelector("#device");
      selector.innerHTML = "";
      for (const device of this._devices) {
        const option = document.createElement("option");
        option.value = device.ieee;
        option.textContent = `${device.name || device.model || device.ieee} (${device.ieee})`;
        selector.appendChild(option);
      }
      if (selectedIeee && this._devices.some((device) => device.ieee === selectedIeee)) {
        selector.value = selectedIeee;
      }
      this.renderDevice();
    } catch (err) {
      this.setStatus(`Failed to load devices: ${err.message || err}`);
    }
  }

  selectedDevice() {
    const ieee = this.querySelector("#device")?.value;
    return (this._devices || []).find((device) => device.ieee === ieee);
  }

  grouped(items) {
    return items.reduce((groups, item) => {
      (groups[item.category] ||= []).push(item);
      return groups;
    }, {});
  }

  renderDevice() {
    const device = this.selectedDevice();
    const content = this.querySelector("#content");
    if (!device) {
      this.setStatus("No supported ZHA devices found.");
      content.innerHTML = "";
      return;
    }
    this.setStatus(`${device.manufacturer || ""} ${device.model || ""} ${device.firmware ? `- Firmware ${device.firmware}` : ""}`);
    const settingGroups = this.grouped(device.settings || []);
    const commandGroups = this.grouped(device.commands || []);
    content.innerHTML = "";
    for (const [category, settings] of Object.entries(settingGroups)) {
      content.appendChild(this.renderSettingsCard(device, category, settings));
    }
    for (const [category, commands] of Object.entries(commandGroups)) {
      content.appendChild(this.renderCommandsCard(device, `${category} commands`, commands));
    }
    content.appendChild(this.renderRawCard(device));
  }

  renderSettingsCard(device, category, settings) {
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `<h2>${category}</h2>`;
    for (const setting of settings) {
      card.appendChild(this.renderSettingRow(device, setting));
    }
    return card;
  }

  renderCommandsCard(device, category, commands) {
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `<h2>${category}</h2>`;
    for (const command of commands) {
      const row = document.createElement("div");
      row.className = "row";
      row.innerHTML = `
        <div>
          <div class="name">${command.name}</div>
          <div class="meta">Cluster 0x${command.cluster_id.toString(16)} • Command 0x${command.command_id.toString(16)}</div>
        </div>
        <span></span>
        <button>Run</button>
      `;
      row.querySelector("button").addEventListener("click", async () => {
        await this._hass.callWS({ type: "zha_advanced_toolkit/command", ieee: device.ieee, key: command.key });
        this.setStatus(`Ran ${command.name}`);
      });
      card.appendChild(row);
    }
    return card;
  }

  renderSettingRow(device, setting) {
    const row = document.createElement("div");
    row.className = "row";
    const input = this.createInput(setting);
    const read = document.createElement("button");
    read.className = "secondary";
    read.textContent = "Read";
    const write = document.createElement("button");
    write.textContent = "Write";
    row.innerHTML = `
      <div>
        <div class="name">${setting.name}</div>
        <div class="meta">Cluster 0x${setting.cluster_id.toString(16)} • Attribute 0x${setting.attribute_id.toString(16)} • ${setting.attribute_name || setting.key}</div>
      </div>
    `;
    row.appendChild(input);
    const buttons = document.createElement("span");
    buttons.appendChild(read);
    buttons.appendChild(write);
    row.appendChild(buttons);
    read.addEventListener("click", async () => {
      await this.readSetting(device, setting, input);
    });
    write.addEventListener("click", async () => {
      await this.writeSetting(device, setting, input);
    });
    this.readSetting(device, setting, input, true);
    return row;
  }

  renderRawCard(device) {
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `
      <h2>Raw cluster access</h2>
      <div class="meta">Use this for attributes that do not have friendly controls yet. Values are written directly through ZHA.</div>
      <div class="raw-grid">
        <label>Endpoint <input id="raw-endpoint" type="number" value="1"></label>
        <label>Cluster type
          <select id="raw-cluster-type">
            <option value="in">in</option>
            <option value="out">out</option>
          </select>
        </label>
        <label>Cluster ID <input id="raw-cluster" value="0xfc31"></label>
        <label>Attribute ID <input id="raw-attribute"></label>
        <label>Manufacturer <input id="raw-manufacturer" value="4655"></label>
        <label>Value <input id="raw-value"></label>
      </div>
      <button class="secondary" id="raw-load">Load exposed clusters</button>
      <button class="secondary" id="raw-read">Read raw</button>
      <button id="raw-write">Write raw</button>
      <div class="raw-list" id="raw-list"></div>
    `;
    card.querySelector("#raw-load").addEventListener("click", () => this.loadRawClusters(device, card));
    card.querySelector("#raw-read").addEventListener("click", () => this.rawRead(device, card));
    card.querySelector("#raw-write").addEventListener("click", () => this.rawWrite(device, card));
    return card;
  }

  createInput(setting) {
    if (setting.type === "select") {
      const select = document.createElement("select");
      for (const opt of setting.options || []) {
        const option = document.createElement("option");
        option.value = opt.value;
        option.textContent = opt.label;
        select.appendChild(option);
      }
      return select;
    }
    if (setting.type === "switch") {
      const select = document.createElement("select");
      for (const opt of [{ value: 0, label: "Off" }, { value: 1, label: "On" }]) {
        const option = document.createElement("option");
        option.value = opt.value;
        option.textContent = opt.label;
        select.appendChild(option);
      }
      return select;
    }
    const input = document.createElement("input");
    input.type = "number";
    input.min = setting.min ?? "";
    input.max = setting.max ?? "";
    input.step = setting.step ?? 1;
    return input;
  }

  async readSetting(device, setting, input, quiet = false) {
    try {
      const result = await this._hass.callWS({ type: "zha_advanced_toolkit/read", ieee: device.ieee, key: setting.key });
      input.value = result.value;
      if (!quiet) this.setStatus(`Read ${setting.name}: ${result.value}`);
    } catch (err) {
      if (!quiet) this.setStatus(`Failed to read ${setting.name}: ${err.message || err}`);
    }
  }

  async writeSetting(device, setting, input) {
    let value = input.value;
    if (setting.type === "number" || setting.type === "select" || setting.type === "switch") {
      value = Number(value);
    }
    try {
      await this._hass.callWS({ type: "zha_advanced_toolkit/write", ieee: device.ieee, key: setting.key, value });
      this.setStatus(`Wrote ${setting.name}: ${value}`);
    } catch (err) {
      this.setStatus(`Failed to write ${setting.name}: ${err.message || err}`);
    }
  }

  parseRawInteger(value) {
    const text = String(value || "").trim();
    if (!text) return undefined;
    const parsed = Number.parseInt(text, text.toLowerCase().startsWith("0x") ? 16 : 10);
    return Number.isNaN(parsed) ? undefined : parsed;
  }

  rawPayload(device, card) {
    const manufacturer = this.parseRawInteger(card.querySelector("#raw-manufacturer").value);
    const endpointId = this.parseRawInteger(card.querySelector("#raw-endpoint").value);
    const clusterId = this.parseRawInteger(card.querySelector("#raw-cluster").value);
    const attributeId = this.parseRawInteger(card.querySelector("#raw-attribute").value);
    if (endpointId === undefined || clusterId === undefined || attributeId === undefined) {
      throw new Error("Endpoint, cluster ID, and attribute ID are required");
    }
    const payload = {
      ieee: device.ieee,
      endpoint_id: endpointId,
      cluster_id: clusterId,
      cluster_type: card.querySelector("#raw-cluster-type").value,
      attribute_id: attributeId,
    };
    if (manufacturer !== undefined) payload.manufacturer = manufacturer;
    return payload;
  }

  async loadRawClusters(device, card) {
    try {
      const clusters = await this._hass.callWS({ type: "zha_advanced_toolkit/raw_clusters", ieee: device.ieee });
      const list = card.querySelector("#raw-list");
      list.innerHTML = clusters.map((cluster) => {
        const attrs = (cluster.attributes || []).map((attr) => `0x${attr.id.toString(16)} ${attr.name}`).join(", ");
        return `<div><b>EP ${cluster.endpoint_id} ${cluster.cluster_type} 0x${cluster.cluster_id.toString(16)}</b> ${cluster.name}: ${attrs || "no attributes listed"}</div>`;
      }).join("");
      this.setStatus(`Loaded ${clusters.length} exposed clusters`);
    } catch (err) {
      this.setStatus(`Failed to load raw clusters: ${err.message || err}`);
    }
  }

  async rawRead(device, card) {
    try {
      const result = await this._hass.callWS({ type: "zha_advanced_toolkit/raw_read", ...this.rawPayload(device, card) });
      card.querySelector("#raw-value").value = result.value;
      this.setStatus(`Read raw value: ${result.value}`);
    } catch (err) {
      this.setStatus(`Failed to read raw value: ${err.message || err}`);
    }
  }

  async rawWrite(device, card) {
    let value = card.querySelector("#raw-value").value;
    const parsed = this.parseRawInteger(value);
    const trimmed = String(value).trim();
    if (parsed !== undefined && /^-?(0x[0-9a-f]+|\d+)$/i.test(trimmed)) value = parsed;
    try {
      await this._hass.callWS({ type: "zha_advanced_toolkit/raw_write", ...this.rawPayload(device, card), value });
      this.setStatus(`Wrote raw value: ${value}`);
    } catch (err) {
      this.setStatus(`Failed to write raw value: ${err.message || err}`);
    }
  }

  setStatus(message) {
    const status = this.querySelector("#status");
    if (status) status.textContent = message;
  }
}

customElements.define("zha-advanced-toolkit-panel", ZhaAdvancedToolkitPanel);
