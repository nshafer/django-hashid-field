# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) 
and this project adheres to [Semantic Versioning](http://semver.org/).

## [3.2.0] - 2021-03-15
### Added
- Added optional string prefixes to generated hashids. e.g. "rec_8ghK0LM".
  (Thanks [Brendan McCollam](https://github.com/bjmc))
- Added BigHashidField and AutoBigHashidField
- Added new global and per-field option to disable the Hashid object, and instead return plain hashid strings for
  increased compatibility.
- Added new global and per-field option to disable the descriptor for increased compatibility.
- Added Global HASHID_FIELD_MIN_LENGTH and HASHID_FIELD_ALPHABET settings.
- Added Support for Django 3.1
- Added (BETA) support for Django 3.2, which is currently in Beta.
- Added a note per [Issue #51](https://github.com/nshafer/django-hashid-field/issues/51) about the hashids-python
  library only caring about the first 43 characters. Thanks [Ralph Bolton](https://github.com/coofercat).
### Changes
- Documented per-field salt usage for unique hashids.
- Optimized Hashid instantiation by testing for integer before hashid decode.
- Optimized lookups by testing for integer instead of hashid decode.
### Removed
- Removed deprecation warnings for HASHID_FIELD_ALLOW_INT and `allow_int`
- Removed support for Django 1.11 which is EOL

## [3.1.3] - 2020-06-05
### Changes
- Check passed alphabet for length and that the characters are unique.

## [3.1.2] - 2020-05-28
### Changes
- [#40]: Use a single instance of the Hashids class for all instances of a given Hashid*Field. In testing, this decreased
  time taken to instantiate those rows by about 63%, and memory usage is drastically decreased.
  (Thanks [Alexandru Chirila](https://github.com/alexkiro))

## [3.1.1] - 2020-01-15
### Fixes
- Fixed security bug where comparison operators (gt, gte, lt, lte) would allow integer lookups regardless of
  ALLOW_INT_LOOKUP setting.
- Fixed tests that were relying on allow_int_lookup to be set in other tests.

## [3.1.0] - 2020-01-14
### Changes
- Added support for `gt`, `gte`, `lt` and `lte` lookups.
  - Example: `MyModel.objects.filter(id__gt=100)` (If `allow_int_lookups` is True)
  - Example: `MyModel.objects.filter(id__gt="Ba9p1AG")`
  - (Thanks for report from [frossigneux](https://github.com/frossigneux) in Issue [#38]

## [3.0.0] - 2019-12-05
### Changes
- Dropped Python 2.7 support. 
- Added Python 3.8 support. 
- Added official support for Django 3.0
- Added official support for Django Rest Framework 3.10.
- (Thanks [hhamana](https://github.com/hhamana))

## [2.1.6] - 2019-04-02
### Changes
- Added official support for Django 2.2 LTS.
- Added official support for Django Rest Framework 3.9.
- Deprecated support for Django 2.0 as it is no longer a maintained version of Django. However, the library will most
  likely continue to work with it for the time being as nothing else has changed.

## [2.1.5] - 2018-10-31
### Changes
- [#29] / [#30]: Fixed exception when decoding a Hashids value of 0.
         (Thanks [Lee H](https://github.com/fpghost))

## [2.1.4] - 2018-10-05
### Changes
- [#27]: Fixed PendingDeprectationWarning for `context` in `from_db_value()`.
         (Thanks [Adam Johnson](https://github.com/adamchainz))

## [2.1.3] - 2018-09-21
### Changes
- [#26]: Fixed version import error. (Thanks [Dido Arellano](https://github.com/didoarellano))

## [2.1.2] - 2018-09-11
### Changes
- [#24]: Added official support for Django 2.1. (Thanks [Adam Tokarski](https://github.com/adam-tokarski))
- Deprecated support for Python 3.5, Django 1.8 - 1.10. Next major release will drop support completely.
- Updated Django Rest Framework support to 3.8.
- Clarified README (Issue #23)

## [2.1.1] - 2018-03-15
### Changes
- Update documentation for DRF integration

## [2.1.0] - 2017-12-10
### Changes
- Added support for pickling Hashid instances (Thanks [Oleg Pesok](https://github.com/olegpesok))
- Add `long` comparisons for python2 (Thanks [Oleg Pesok](https://github.com/olegpesok))
- Add support for Django 2.0. (Thanks [Paul Nakata](https://github.com/pmn))

Please note: 1.8 will be supported until April at least (same as Django), but after that we may support only
Django 1.11 and 2.0, per Django's recommendations and release schedule.

Django Rest Framework has dropped support for Django 1.8 and 1.9 as of their 3.7.x line, and there are import bugs
with 1.11 and DRF 3.7.3, so we are supporting (and testing) DRF 3.6.4 for Django 1.8 -> 1.11, and DRF 3.7 for 2.0.

## [2.0.1] - 2017-10-04
### Changes
- Field option 'allow_int' renamed to 'allow_int_lookup' to be more descriptive. Using 'allow_int' will print
  a DeprecationWarning and will be removed in a future version.
- Global setting `HASHID_FIELD_ALLOW_INT` renamed to `HASHID_FIELD_ALLOW_INT_LOOKUP` to be more descriptive. Setting
  `HASHID_FIELD_ALLOW_INT` will print a DeprecationWarning and will be removed in a future version.
- Instances of the Hashid class are now immutable to conform to the Python Data Model and hashing behavior.
  This should be invisible to any typical uses.
  
### Potentially Breaking Changes
- Integer lookups are now disabled by default. Set `HASHID_FIELD_ALLOW_INT_LOOKUP=True` or `allow_int_lookup=True` to
  revert to previous behavior. Saving integers is always supported regardless of the setting or parameter.
- Lookups with invalid Hashids strings (or integers if integer lookups is disabled) now returns no results by default
  instead of throwing an exception. This will mean fewer exceptions being throw due to user input, and will also allow
  Hashid*Fields to be used in the Django ModelAdmin `search_fields` parameter without throwing exceptions.
  Set the new global setting `HASHID_FIELD_LOOKUP_EXCEPTION=True` to revert to the
  older behavior of throwing an exception when an invalid Hashid string or integer is given in lookups.
  Saving an invalid hashid string will always result in a ValueError being thrown.
- The field will now throw a ValueError instead of TypeError when attempting to save (or lookup, if lookup exceptions
  are enabled) an invalid hashid string.

### Upgrading
- Integer lookups are now disabled by default, so if you are setting it to False, then you can just remove the setting
  and/or parameters.
- Rename the setting `HASHID_FIELD_ALLOW_INT=True` to `HASHID_FIELD_ALLOW_INT_LOOKUP=True`
- Rename any instances of the parameter `allow_int=True` to `allow_int_lookup=True` in Hashid*Field definitions.
- You can remove any traps for TypeError when doing lookups, or conversely if you rely on the behavior, then set
  `HASHID_FIELD_LOOKUP_EXCEPTION=True` in your project settings, and catch ValueError now instead of TypeError.

## [1.3.0] - 2017-09-25
### Changed
- Created custom Lookup system that supports Int, String and better restricts Int lookups if ALLOW_INT=False
  Thanks to Oskar Persson (https://github.com/OskarPersson)
- Allow comparison with strings.
  Thanks to Gordon Wrigley (https://github.com/tolomea)
- Updated dependencies to latest versions (Hashids 1.2.0, DRF 3.6.4)

### Added
- Added documentation for setting up Development environment.
- Added official LICENSE (MIT)

### Fixed
- Fixed hashing functionality to conform to Python Data Model.
- Fixed bug when setting descriptor after a set operation failed.

## [1.2.3] - 2017-07-22
### Changed
- Added ability for Hashid instances to be typecast to integers.
  Thanks to Michael Lavers (https://github.com/kolanos)

## [1.2.2] - 2017-06-13
### Changed
- Fixed bug with Django 1.11.2 causing the error "AttributeError: 'NoneType' object has no attribute '__dict__'"
  Thanks to Kit La Touche (https://github.com/wlonk)

## [1.2.1] - 2017-02-21
### Changed
- Fixed bug with Django Admin on 1.11 not using correct Widget

## [1.2.0] - 2017-02-21
### Added
- Added setting for turning off integer lookups
- Added documentation on how to use Hashid*Fields with DRF's PrimaryKeyRelatedField

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

[3.1.3]: https://github.com/nshafer/django-hashid-field/compare/3.1.3...3.2.0
[3.1.3]: https://github.com/nshafer/django-hashid-field/compare/3.1.2...3.1.3
[3.1.2]: https://github.com/nshafer/django-hashid-field/compare/3.1.1...3.1.2
[3.1.1]: https://github.com/nshafer/django-hashid-field/compare/3.1.0...3.1.1
[3.1.0]: https://github.com/nshafer/django-hashid-field/compare/3.0.0...3.1.0
[3.0.0]: https://github.com/nshafer/django-hashid-field/compare/2.1.6...3.0.0
[2.1.6]: https://github.com/nshafer/django-hashid-field/compare/2.1.5...2.1.6
[2.1.5]: https://github.com/nshafer/django-hashid-field/compare/2.1.4...2.1.5
[2.1.4]: https://github.com/nshafer/django-hashid-field/compare/2.1.3...2.1.4
[2.1.3]: https://github.com/nshafer/django-hashid-field/compare/2.1.2...2.1.3
[2.1.2]: https://github.com/nshafer/django-hashid-field/compare/2.1.1...2.1.2
[2.1.1]: https://github.com/nshafer/django-hashid-field/compare/2.1.0...2.1.1
[2.1.0]: https://github.com/nshafer/django-hashid-field/compare/2.0.1...2.1.0
[2.0.1]: https://github.com/nshafer/django-hashid-field/compare/1.3.0...2.0.1
[1.3.0]: https://github.com/nshafer/django-hashid-field/compare/1.2.3...1.3.0
[1.2.3]: https://github.com/nshafer/django-hashid-field/compare/1.2.2...1.2.3
[1.2.2]: https://github.com/nshafer/django-hashid-field/compare/1.2.1...1.2.2
[1.2.1]: https://github.com/nshafer/django-hashid-field/compare/1.2.0...1.2.1
[1.2.0]: https://github.com/nshafer/django-hashid-field/compare/1.1.0...1.2.0
[1.1.0]: https://github.com/nshafer/django-hashid-field/compare/1.0.1...1.1.0
[1.0.1]: https://github.com/nshafer/django-hashid-field/compare/1.0.0...1.0.1
[1.0.0]: https://github.com/nshafer/django-hashid-field/compare/0.1.6...1.0.0

[#24]: https://github.com/nshafer/django-hashid-field/pull/24
[#26]: https://github.com/nshafer/django-hashid-field/pull/26
[#27]: https://github.com/nshafer/django-hashid-field/issues/27
[#29]: https://github.com/nshafer/django-hashid-field/issues/29
[#30]: https://github.com/nshafer/django-hashid-field/pull/30
[#38]: https://github.com/nshafer/django-hashid-field/issues/38
[#40]: https://github.com/nshafer/django-hashid-field/pull/40
