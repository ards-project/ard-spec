---
title: Agent Finder — Federated Search and Discovery for AI Capabilities
hide:
  - navigation
  - toc
---

<div class="landing-page">

  <!-- Ambient Glows -->
  <div class="glow-sphere glow-1"></div>
  <div class="glow-sphere glow-2"></div>

  <!-- Hero Section -->
  <div class="hero-container">
<div class="hero-text">
  <h1>Discover AI Capabilities <span class="hero-title-gradient">Federated & Search-First</span></h1>
  <p class="hero-subtitle">
    Agent Finder is a standardized, domain-anchored discovery specification designed to catalog, search, and discover AI capabilities (MCP servers, A2A cards, skills, and services) across federated networks.
  </p>
  <div class="hero-buttons">
    <a href="why/" class="btn btn-primary">Why It's Needed</a>
    <a href="spec/" class="btn btn-secondary">Read the Specification</a>
  </div>
</div>

    <!-- Code Window -->
    <div class="mac-window">
      <div class="window-header">
        <div class="window-dot dot-red"></div>
        <div class="window-dot dot-yellow"></div>
        <div class="window-dot dot-green"></div>
        <div class="window-title">ai-catalog.json</div>
      </div>
      <div class="window-body">
<pre><span class="kw">{</span>
  <span class="str">"specVersion"</span>: <span class="str">"1.0"</span>,
  <span class="str">"host"</span>: <span class="kw">{</span>
    <span class="str">"displayName"</span>: <span class="str">"Acme AI"</span>,
    <span class="str">"identifier"</span>: <span class="str">"did:web:acme.com"</span>
  <span class="kw">}</span>,
  <span class="str">"entries"</span>: <span class="kw">[</span>
    <span class="kw">{</span>
      <span class="str">"identifier"</span>: <span class="str">"urn:ai:acme:agent:trading"</span>,
      <span class="str">"displayName"</span>: <span class="str">"Finance Trading Agent"</span>,
      <span class="str">"type"</span>: <span class="str">"application/a2a-agent-card+json"</span>,
      <span class="str">"url"</span>: <span class="str">"https://api.acme.com/agent.json"</span>,
      <span class="str">"representativeQueries"</span>: <span class="kw">[</span>
        <span class="str">"analyze market trend for 2026"</span>
      <span class="kw">]</span>
    <span class="kw">}</span>
  <span class="kw">]</span>
<span class="kw">}</span></pre>
      </div>
    </div>
  </div>

  <!-- Features Section -->
  <div class="features-section">
    <div class="features-section-header">
      <h2>Why Agent Finder?</h2>
      <p>Architected to solve discovery, scaling, trust, and interop problems for LLMs at global scale.</p>
    </div>

    <div class="features-grid">
      <div class="feature-card">
        <div class="feature-icon">🔍</div>
        <h3>Search-First Discovery</h3>
        <p>Discover capabilities dynamically at runtime via queries, rather than using pre-installed or hardcoded lists.</p>
      </div>

      <div class="feature-card">
        <div class="feature-icon">⚡</div>
        <h3>Context Scalability</h3>
        <p>Externalize semantic rank computation to dedicated search indexes, scaling to millions of tools without token bloat.</p>
      </div>

      <div class="feature-card">
        <div class="feature-icon">🛡️</div>
        <h3>Progressive Trust Layers</h3>
        <p>Verifiable identity anchors linked with SOC2/GDPR compliance attestations and detached signatures.</p>
      </div>

      <div class="feature-card">
        <div class="feature-icon">🌐</div>
        <h3>Universal Federation</h3>
        <p>Standardized HTTP REST search interfaces coordinate upstream nodes, providing unified results instantly.</p>
      </div>
    </div>
  </div>

</div>
