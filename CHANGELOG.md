# CHANGELOG

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
