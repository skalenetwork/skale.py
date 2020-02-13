# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - Unreleased

### Added

- Delegation functionality
- Validator functionality

## [2.0.0] - 2019-10-05

### Added

- This CHANGELOG file.
- Multithreading tests.
- Transactions Manager support.

### Changed

- All `web3` related functions moved from `skale.utils.helper` to `skale.utils.web_utils`.
- `skale.utils.helper.await_receipt` renamed to `skale.utils.web3_utils.wait_receipt`.
- `get_provider` method moved from `Skale` class to the `web3_utils`.
- `sign_and_send` signature is changed - wallet param is now optional. 
- `@format` decorator renamed to `@format_fields`.
- Updated tests.

### Fixed

- Web3 work in multiple threads.

### Removed

- All functionality around local nonce management.
- Unused `RELEASES.md` file.
