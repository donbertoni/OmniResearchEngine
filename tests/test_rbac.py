from omni.domain.rbac import role_capabilities


def test_owner_can_do_everything():
    caps = role_capabilities("owner")
    assert caps.can_manage_members
    assert caps.can_manage_billing
    assert caps.can_manage_credentials
    assert caps.can_edit_triggers


def test_admin_cannot_manage_billing():
    caps = role_capabilities("admin")
    assert caps.can_manage_members
    assert caps.can_manage_billing is False
    assert caps.can_edit_automations


def test_analyst_can_edit_but_not_manage_members_or_credentials():
    caps = role_capabilities("analyst")
    assert caps.can_edit_triggers
    assert caps.can_edit_asset_pools
    assert caps.can_manage_members is False
    assert caps.can_manage_credentials is False


def test_viewer_can_do_nothing():
    caps = role_capabilities("viewer")
    assert not any([
        caps.can_manage_members, caps.can_manage_billing, caps.can_manage_credentials,
        caps.can_edit_triggers, caps.can_edit_automations, caps.can_edit_asset_pools,
    ])


def test_unknown_role_fails_safe_as_viewer():
    assert role_capabilities("bogus-role") == role_capabilities("viewer")
    assert role_capabilities("") == role_capabilities("viewer")
