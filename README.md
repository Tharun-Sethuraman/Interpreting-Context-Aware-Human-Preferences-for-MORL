# Interpreting Context-Aware Human Preferences for Multi-Objective Robot Navigation
Tharun Sethuraman<sup>1</sup>, Subham Agrawal<sup>2,3</sup>, Nils Dengler<sup>2,3</sup>, Jorge de Heuvel<sup>2</sup>, Teena Hassan<sup>1</sup>, and Maren Bennewitz<sup>2,3</sup>

## Abstract
<p>
Robots operating in human-shared environments must not only achieve task-level navigation objectives such as safety and efficiency, but also adapt their behavior to human preferences. However, as human preferences are typically expressed in natural language and depend on environmental context, it is difficult to directly integrate them into low-level robot control policies. In this work, we present a pipeline that enables robots to understand and apply context-dependent navigation preferences by combining foundational models with a Multi-Objective Reinforcement Learning (MORL) navigation policy. Thus, our approach integrates high-level semantic reasoning with low-level motion control.  A Vision-Language Model (VLM) extracts structured environmental context from onboard visual observations, while Large Language Models (LLM) convert natural language user feedback into interpretable, context-dependent behavioral rules stored in a persistent but updatable rule memory. A preference translation module then maps contextual information and stored rules into numerical preference vectors that parameterize a pretrained MORL policy for real-time navigation adaptation. We evaluate the proposed framework through quantitative component-level evaluations, a user study, and real-world robot deployments in various indoor environments. Our results demonstrate that the system reliably captures user intent, generates consistent preference vectors, and enables controllable behavior adaptation across diverse contexts. Overall, the proposed pipeline improves the adaptability, transparency, and usability of robots operating in shared human environments, while maintaining safe and responsive real-time control.
</p>

## Architecture
<img width="4178" height="1483" alt="architecture (1)" src="https://github.com/user-attachments/assets/7a2314d9-02d3-4a2a-9cca-a1ece1f86c7b" />

