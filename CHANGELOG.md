# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) 
and this project adheres to [Semantic Versioning](http://semver.org/).

## [2.1.0] - 2017-12-10
### Changes
- Added support for pickling Hashid instances
- Add `long` comparisons for python2
- Add support for Django 2.0.

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
