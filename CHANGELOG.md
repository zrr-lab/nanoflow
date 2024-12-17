# CHANGELOG

## v0.9.0 (2024-12-17)

### ✨ feat

* ✨ feat: add functionality for getting available resources by utilization ([`7c5f095`](https://github.com/zrr-lab/nanoflow/commit/7c5f0959db79b90247b130a77283080146d23c4d))

### 🐛 fix

* 🐛 fix: fix task matrix when `workflow.matrix` is `None` ([`27da9a5`](https://github.com/zrr-lab/nanoflow/commit/27da9a5f1f5fb3696e93289fe9104fdc0dbe1377))

### 📝 docs

* 📝 docs: update readme ([`f7739ee`](https://github.com/zrr-lab/nanoflow/commit/f7739ee5b2ea2aef5c575ebfeff92cb147adb2c1))

## v0.8.0 (2024-11-03)

### ♻️ refactor

* ♻️ refactor: change command name `generate_commands` to `try_run` and add arg for run command ([`863804b`](https://github.com/zrr-lab/nanoflow/commit/863804bf1b38cf97816198cd0292cd88d601eb45))

### ✨ feat

* ✨ feat: add `DynamicResourcePool` and `GPUResourcePool` ([`f650d87`](https://github.com/zrr-lab/nanoflow/commit/f650d8729f8f95f66e1307f45351ab8d454bb451))

### ⬆️ deps

* ⬆️ deps: upgrade python to 3.12 ([`4c1c664`](https://github.com/zrr-lab/nanoflow/commit/4c1c664be72f500269500ab09d9f603ae5a6131a))

## v0.7.0 (2024-10-22)

### ✨ feat

* ✨ feat: add support for generate-commands ([`83de3ed`](https://github.com/zrr-lab/nanoflow/commit/83de3edab873cd6a9630a3ab2908f3da6fbbf625))

## v0.6.0 (2024-10-22)

### ♻️ refactor

* ♻️ refactor: format task name based on its own matrix ([`687e65b`](https://github.com/zrr-lab/nanoflow/commit/687e65badabb225029933c967e58d2c7fe0655d0))

### ✨ feat

* ✨ feat: add basic `Executor` ([`c5b8d87`](https://github.com/zrr-lab/nanoflow/commit/c5b8d877387b5301d84090de0e36857af13571f1))

* ✨ feat: add `UnlimitedPool` ([`6bd4f0b`](https://github.com/zrr-lab/nanoflow/commit/6bd4f0bc52bf2f4df30850a7a32e2773703ced84))

## v0.5.2 (2024-10-20)

### ✅ test

* ✅ test: add tests for error handling ([`181f540`](https://github.com/zrr-lab/nanoflow/commit/181f5402bd9c6d3ae8ac180927cb7add5c1bdda3))

* ✅ test: add more tests for task config ([`1346f48`](https://github.com/zrr-lab/nanoflow/commit/1346f48323520f38c33984ca7b1700ac08d66638))

### 🐛 fix

* 🐛 fix: fix issue where task does not execute when `resource_pool` is `None` ([`42603ac`](https://github.com/zrr-lab/nanoflow/commit/42603ac017383608dbaad7dca1c482c9b149bff6))

## v0.5.1 (2024-10-19)

### ⚡ perf

* ⚡ perf: improve user experience with clearer log messages ([`0c20b5d`](https://github.com/zrr-lab/nanoflow/commit/0c20b5d2a698138183117259661ef4cdd5731e1b))

### 📝 docs

* 📝 docs: update README ([`c6a4aa7`](https://github.com/zrr-lab/nanoflow/commit/c6a4aa7d5dbf3adbe4c07dc92688154607e8f745))

## v0.5.0 (2024-10-18)

### ✨ feat

* ✨ feat: support `matrix` in task config ([`f7430a3`](https://github.com/zrr-lab/nanoflow/commit/f7430a3cd1a56221ab9b1660438a4c9b572d1c25))

## v0.4.0 (2024-10-18)

### ✨ feat

* ✨ feat: support `matrix` in flow config ([`a0218d5`](https://github.com/zrr-lab/nanoflow/commit/a0218d563098ee133c17524d3c527ec64a07575c))

## v0.3.0 (2024-10-18)

### ♻️ refactor

* ♻️ refactor: move some cli code to `cli.py` ([`c86b839`](https://github.com/zrr-lab/nanoflow/commit/c86b839b3e1a60a76653af68d1cdbece064e90f2))

### ✨ feat

* ✨ feat: support `args` in task config ([`196fb80`](https://github.com/zrr-lab/nanoflow/commit/196fb809671f369099252d9de5a213a8cda35173))

### 👷 ci

* 👷 ci: improve release ([`d903e31`](https://github.com/zrr-lab/nanoflow/commit/d903e31921d5c92e5e61d17175af67c019e39d0e))

### 📝 docs

* 📝 docs: update readme ([`5939118`](https://github.com/zrr-lab/nanoflow/commit/59391183b1ce531f22db498cbdf1b48271b5119c))

### 🔧 chore

* 🔧 chore: update README and add LICENCE ([`739888d`](https://github.com/zrr-lab/nanoflow/commit/739888dee5fc25fb1228b4d43450e33e765692de))

## v0.2.0 (2024-10-08)

### ✨ feat

* ✨ feat: support custom resources in config (#2) ([`f4c3175`](https://github.com/zrr-lab/nanoflow/commit/f4c3175df5a2d3a93f2b1f9d07e3f64f92ec47f2))

### 👷 ci

* 👷 ci: add codspeed action ([`432d331`](https://github.com/zrr-lab/nanoflow/commit/432d3316fda5ddb1483b376c6e1979fbf7627678))

* 👷 ci: add issue auto comments and issues translate ([`ec70cf6`](https://github.com/zrr-lab/nanoflow/commit/ec70cf65ffddd739d9e5e69f58e8ef73f17cd3df))

### 🔧 chore

* 🔧 chore: improve log ([`92b521e`](https://github.com/zrr-lab/nanoflow/commit/92b521e6f13ca243ac3030cbe0b2393b1f725753))

## v0.1.0 (2024-10-03)

### ♻️ refactor

* ♻️ refactor: rename `execute_gpu_parallel_tasks` to `execute_gpu_parallel_tasks` ([`6e7290b`](https://github.com/zrr-lab/nanoflow/commit/6e7290b6ebf909c05e82d9c78626944f9eee948b))

### ✨ feat

* ✨ feat: add basic tui ([`23a49e1`](https://github.com/zrr-lab/nanoflow/commit/23a49e1259949a0d2e06517d9c9bc78fd3a3cfef))

### 🐛 fix

* 🐛 fix: use uv run in justfile ([`eeb5371`](https://github.com/zrr-lab/nanoflow/commit/eeb5371dfb5184c27fb66dc2f8095f9a57628281))

### 👷 ci

* 👷 ci: fix releaserc ([`8fae1c8`](https://github.com/zrr-lab/nanoflow/commit/8fae1c831160cceac068b606b3492b7f4f3f9db4))

* 👷 ci: organize actions ([`8cf81a5`](https://github.com/zrr-lab/nanoflow/commit/8cf81a50a4052250e5e8b8baf594887566c3b059))

* 👷 ci: add release action ([`b5fd630`](https://github.com/zrr-lab/nanoflow/commit/b5fd6309f16777d5f9664d441744171db77f81c8))

### 📝 docs

* 📝 docs: add examples ([`77ab584`](https://github.com/zrr-lab/nanoflow/commit/77ab58432ddfa7b942821ffeafa0b5f65ce7dafe))

### 🔧 chore

* 🔧 chore: remove version_variables in releaserc ([`e83cf7d`](https://github.com/zrr-lab/nanoflow/commit/e83cf7d24eaf76108893a82eee21bf2c31aefffc))

## v0.0.5 (2024-09-21)

### ✨ feat

* ✨ feat: support retry functionality ([`9e74aa2`](https://github.com/zrr-lab/nanoflow/commit/9e74aa22e560aa80680a234519192f85e885d744))

### 👷 ci

* 👷 ci: add coverage to actions ([`e690f6a`](https://github.com/zrr-lab/nanoflow/commit/e690f6a292e9a67e3b0470731ce7f4bce0fcd2e6))

## v0.0.4 (2024-09-21)

### 🔧 chore

* 🔧 chore: optimize dependency configuration and improve logging ([`f421645`](https://github.com/zrr-lab/nanoflow/commit/f421645af9d0d0867f2634dc1a9a2f34cc5c9553))

## v0.0.3 (2024-09-19)

### 🐛 fix

* 🐛 fix: when the original node in dependencies is also added to the nodes that need to be executed ([`2a5efdf`](https://github.com/zrr-lab/nanoflow/commit/2a5efdf1ca49b479e9a64db2abb5552965cc900b))

## v0.0.2 (2024-09-19)

### ✨ feat

* ✨ feat: add resource_modifier functionality ([`5f8aa29`](https://github.com/zrr-lab/nanoflow/commit/5f8aa29966e7410361b1c688b685e25fe70649b5))

* ✨ feat: add `nanoflow` command line interface ([`4c03741`](https://github.com/zrr-lab/nanoflow/commit/4c03741f3406d96ad87592a47b7271b73f07fc33))

### 👷 ci

* 👷 ci: fix pdm build action ([`0766eac`](https://github.com/zrr-lab/nanoflow/commit/0766eac299928fa9e9f8778a113af0da898102c3))

### 🔧 chore

* 🔧 chore: run pre-commit for formatting ([`768090b`](https://github.com/zrr-lab/nanoflow/commit/768090b6e059ec49cc931bcac0eabe5d724febd3))

## v0.0.1 (2024-09-18)

### 🎉 init

* 🎉 init: init project ([`8350466`](https://github.com/zrr-lab/nanoflow/commit/8350466c0dd45bc9d1c64d8a12b9677baf0f90f5))
