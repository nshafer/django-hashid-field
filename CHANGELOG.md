# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) 
and this project adheres to [Semantic Versioning](http://semver.org/).

## [1.1.0] - 2017-01-25
### Added
- Added support for Django REST Framework serializers.

## [1.0.1] - 2016-12-28
### Changed
- Updated install documentation to suggest adding HASHID_FIELD_SALT on install.

## [1.0.0] - 2016-12-27
### Changed
- (Breaking change) Salt no longer uses settings.SECRET_KEY
- HashidField and HashidAutoField use `salt=settings.HASHID_FIELD_SALT` by default

### Added
- HASHID_FIELD_SALT in Django settings for global salt value for all HashidFields and
  HashidAutoFields
- Django checks warning if salt is not specified globally or on each individual field.

### Upgrading
- If you already specified `salt` in fields, like `id = HashidField(salt="something")` everywhere
  then you're already set, and can upgrade worry-free.
- If you instead let the module fallback to `salt=settings.SECRET_KEY` (default behavior) then this
  upgrade will change all of your existing fields. It has been pointed out by @fjsj that it's possible
  to discover the salt used when encoding Hashids, and thus it is very dangerous to use
  settings.SECRET_KEY, as an attacker may be able to get your SECRET_KEY from your HashidFields.
- If you absolutely MUST maintain backwards-compatibility and continue to support your old hashed
  values, then you can set `HASHID_FIELD_SALT = SECRET_KEY` in your settings. But this is *VERY
  DISCOURAGED*.

## 0.1.6 - 2016-10-04
### Added
- Initial release

[1.1.0]: https://github.com/nshafer/django-hashid-field/compare/1.0.1...1.1.0
[1.0.1]: https://github.com/nshafer/django-hashid-field/compare/1.0.0...1.0.1
[1.0.0]: https://github.com/nshafer/django-hashid-field/compare/0.1.6...1.0.0
