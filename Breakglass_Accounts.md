PROTECTED ACCOUNT CREDENTIALS — secure these immediately

Username	Role	Type	Password
rfu_dev_always	dev	always_available	ApHfTzB%Sbh^olRX9oSo*ckP
rfu_admin_always	admin	always_available	9ej$XwR_l$Dib$vVKGWZf#O@
rfu_dev_breakglass	dev	break_glass	o3tzq%PfxF%*AWXgqqp5WvZo
rfu_admin_breakglass	admin	break_glass	HtFyPZ8bI6aR!3ItFwCyVYLd

Credentials are also saved to protected_credentials.txt.

Both always-available accounts were created in the bootstrap. Here they are:

Username	Role	Type	Password
rfu_dev_always	dev	always_available	ApHfTzB%Sbh^olRX9oSo*ckP
rfu_admin_always	admin	always_available	9ej$XwR_l$Dib$vVKGWZf#O@
These are distinct from the break-glass accounts in how they behave:

Always-available (is_always_available=True): If the account gets locked out, it automatically unblocks after a 15-minute cooldown — no manual intervention needed. This is the primary lockout-prevention path.
Break-glass (is_break_glass=True): Emergency-only. Requires RFU_ENABLE_BREAK_GLASS=true env var + a justification string (≥10 chars). Every login is fully audited.
Credentials are saved to protected_credentials.txt. All four accounts have reset_required=True — they'll require a password change on first login.