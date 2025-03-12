Create a rule at `./specs/prompts/0-create-project-structure.md` that defines the project structure at the root of the project.


The project should use the following monorepo structure for python.
```
├── dev-requirements.txt
├── infra
│   ├── environments
│   │   ├── dev
│   │   └── prod
│   └── modules
├── libs
│   └── base
│       ├── requirements.txt
│       └── run.sh
├── pip-requirements.txt
├── projects
│   └── transcribe-module
│       ├── specs
│       ├── src
│       └── tests
├── samples
│   └── sample.mp3
└── specs
    └── prompts
```    