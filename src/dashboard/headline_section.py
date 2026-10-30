from .dashboard_section import DashboardSection


class HeadlineSection(DashboardSection):
    """
    The headline figures for the selected loans, one card each.
    """

    title = "Headline figures"

    def header(self, view):
        summary = view.summary
        cards = [("Loans", f"{summary['loans']:,}"), ("Outstanding (UGX)", f"{summary['outstanding']:,}"),
                 ("PAR30", f"{summary['PAR30 %']}%"), ("PAR90", f"{summary['PAR90 %']}%"),
                 ("Average PD", f"{summary['average PD %']}%"),
                 ("Expected loss (UGX)", f"{summary['expected loss']:,}"),
                 ("Payments in period (UGX)", f"{summary['payments received']:,}"),
                 ("Promise keep rate", f"{summary['promise keep rate %']}%")]
        boxes = "".join(f"<div style='border:1px solid #d0d7de;padding:8px 12px;margin:4px;min-width:120px'>"
                        f"<div style='font-size:0.8em;color:#57606a'>{label}</div><div style='font-size:1.3em'>"
                        f"<b>{value}</b></div></div>" for label, value in cards)
        return super().header(view) + f"<div style='display:flex;flex-wrap:wrap'>{boxes}</div>"
