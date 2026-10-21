import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import PIL.Image

def create_architecture_diagram(output_path="docs/architecture_diagram.png"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 1. Canvas Setup: Landscape Word Document Page Simulation
    fig_w, fig_h = 24.0, 14.5
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=150)
    
    # Outer desktop / workspace background (subtle light slate gray)
    fig.patch.set_facecolor('#EEF2F6')
    ax.set_facecolor('#EEF2F6')

    # Document Page: White sheet with subtle drop-shadow effect
    shadow = Rectangle((0.6, 0.4), 22.8, 13.5, facecolor='#CBD5E1', edgecolor='none', zorder=1)
    ax.add_patch(shadow)
    
    page = Rectangle((0.45, 0.55), 22.8, 13.5, facecolor='#FFFFFF', edgecolor='#94A3B8', linewidth=1.2, zorder=2)
    ax.add_patch(page)

    # Document Header / Letterhead Bar (Corporate Navy)
    doc_header = FancyBboxPatch((0.8, 12.65), 22.1, 1.15, boxstyle="round,pad=0.08,rounding_size=0.1",
                                facecolor='#0F172A', edgecolor='#1E293B', linewidth=1.5, zorder=3)
    ax.add_patch(doc_header)

    ax.text(1.2, 13.38, "SAVANNAH INFORMATICS  |  CLINICAL HEALTH PLATFORM", 
            fontsize=15, fontweight='bold', color='#FFFFFF', va='center', zorder=4, family='sans-serif')
    ax.text(1.2, 12.98, "System Design & AWS Cloud Architecture Specification (FastAPI • PostgreSQL • Terraform IaC • CI/CD)", 
            fontsize=10.5, color='#94A3B8', va='center', zorder=4, family='sans-serif')

    ax.text(22.5, 13.38, "DOC ID: ARCH-AWS-2026", fontsize=10, fontweight='bold', color='#38BDF8', ha='right', va='center', zorder=4)
    ax.text(22.5, 12.98, "STATUS: PRODUCTION LIVE  |  AWS APP RUNNER", fontsize=9, color='#A7F3D0', ha='right', va='center', zorder=4)

    # Helper: Load and scale logo image
    def add_logo(x, y, logo_name, zoom=0.22, zorder=6):
        path = f"docs/logos/{logo_name}.png"
        if os.path.exists(path):
            img = PIL.Image.open(path)
            img = img.convert("RGBA")
            imagebox = OffsetImage(img, zoom=zoom)
            ab = AnnotationBbox(imagebox, (x, y), frameon=False, zorder=zorder)
            ax.add_artist(ab)

    # Helper: Node with Logo on top and Name below it
    def draw_component_card(x, y, w, h, title, subtitle_lines, badge_text, logo_name=None, 
                            bg_color='#FFFFFF', border_color='#CBD5E1', badge_color='#0284C7', logo_zoom=0.2):
        # Card Body
        card = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.12",
                              facecolor=bg_color, edgecolor=border_color, linewidth=1.6, zorder=4)
        ax.add_patch(card)

        # Category Badge Header
        badge = FancyBboxPatch((x + 0.15, y + h - 0.38), w - 0.3, 0.28, boxstyle="round,pad=0.04,rounding_size=0.06",
                               facecolor=badge_color, edgecolor='none', zorder=5)
        ax.add_patch(badge)
        ax.text(x + w/2, y + h - 0.24, badge_text, fontsize=8, fontweight='bold', color='#FFFFFF', ha='center', va='center', zorder=6)

        if logo_name:
            logo_y = y + h - 0.95
            add_logo(x + w/2, logo_y, logo_name, zoom=logo_zoom, zorder=6)
            
            # Component Name below logo
            ax.text(x + w/2, y + h - 1.52, title, fontsize=10.5, fontweight='bold', color='#0F172A', ha='center', va='center', zorder=6)
            
            # Subtitle lines below title
            sub_y = y + h - 1.85
            for line in subtitle_lines:
                ax.text(x + w/2, sub_y, line, fontsize=8.2, color='#475569', ha='center', va='top', zorder=6)
                sub_y -= 0.27
        else:
            # Clean layout for client cards
            ax.text(x + w/2, y + h - 0.65, title, fontsize=10.5, fontweight='bold', color='#0F172A', ha='center', va='center', zorder=6)
            sub_y = y + h - 0.95
            for line in subtitle_lines:
                ax.text(x + w/2, sub_y, line, fontsize=8.2, color='#475569', ha='center', va='top', zorder=6)
                sub_y -= 0.26

    # Helper: Boundary Zone
    def draw_zone(x, y, w, h, title, bg_color='#F8FAFC', border_color='#CBD5E1', title_color='#1E293B'):
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.12,rounding_size=0.18",
                             facecolor=bg_color, edgecolor=border_color, linewidth=1.8, linestyle='--', zorder=3)
        ax.add_patch(box)
        badge_w = len(title) * 0.16 + 0.6
        badge = FancyBboxPatch((x + 0.3, y + h - 0.34), badge_w, 0.32,
                               boxstyle="round,pad=0.04,rounding_size=0.08", facecolor=title_color, edgecolor='none', zorder=4)
        ax.add_patch(badge)
        ax.text(x + 0.3 + badge_w/2, y + h - 0.18, title, fontsize=8.8, fontweight='bold', color='#FFFFFF', ha='center', va='center', zorder=5)

    # =========================================================================
    # ZONE 1: CLIENTS & CONSUMERS (Left Top)
    # =========================================================================
    draw_zone(0.9, 7.6, 4.4, 4.7, "1. CONSUMERS & API CLIENTS", bg_color='#F0F9FF', border_color='#0284C7', title_color='#0284C7')
    
    draw_component_card(1.15, 10.7, 3.9, 1.25, "Patients & Web Portal", 
                        ["• Outpatient booking & cancel", "• Dynamic real-time slot view"], 
                        "PATIENT ACCESS", None, bg_color='#FFFFFF', border_color='#93C5FD', badge_color='#0284C7')
    
    draw_component_card(1.15, 9.25, 3.9, 1.25, "Swagger / OpenAPI Docs", 
                        ["• Interactive endpoint UI", "• Inspect schemas at /docs"], 
                        "API EXPLORER", None, bg_color='#FFFFFF', border_color='#93C5FD', badge_color='#0284C7')
    
    draw_component_card(1.15, 7.8, 3.9, 1.25, "Clinic Admin Console", 
                        ["• Doctor shift scheduling", "• Appointment audit logs"], 
                        "STAFF OPERATIONS", None, bg_color='#FFFFFF', border_color='#93C5FD', badge_color='#0284C7')

    # =========================================================================
    # ZONE 2: DEVOPS & INFRASTRUCTURE AS CODE (Left Bottom)
    # =========================================================================
    draw_zone(0.9, 2.0, 7.6, 4.8, "2. TERRAFORM (IaC) & CI/CD PIPELINE", bg_color='#FAF5FF', border_color='#9333EA', title_color='#7E22CE')
    
    # Terraform Card
    draw_component_card(1.15, 2.25, 3.5, 4.1, "HashiCorp Terraform", 
                        ["AWS Cloud Declarations:", "• Amazon ECR Repository", "• AWS App Runner Service", "• AppRunnerECRAccessRole", "• 100% Free-Tier Parameters", "terraform/ module (main.tf)"], 
                        "INFRASTRUCTURE AS CODE", "terraform",
                        bg_color='#FFFFFF', border_color='#C084FC', badge_color='#7B42BC', logo_zoom=0.18)
    
    # GitHub Actions Card
    draw_component_card(4.8, 2.25, 3.5, 4.1, "GitHub Actions CI/CD", 
                        ["Automated Workflow:", "• Branching: main, dev, PRs", "• Run 15 Pytest Test Suite", "• Concurrency collision tests", "• Build & Push Docker image", "• Continuous Deployment"], 
                        "CI/CD AUTOMATION", "github",
                        bg_color='#FFFFFF', border_color='#C084FC', badge_color='#24292E', logo_zoom=0.18)

    # =========================================================================
    # ZONE 3: CONTAINER REGISTRY (Middle Bottom)
    # =========================================================================
    draw_zone(8.8, 2.0, 4.3, 4.8, "3. CONTAINER REGISTRY", bg_color='#FFF7ED', border_color='#EA580C', title_color='#C2410C')
    draw_component_card(9.05, 2.25, 3.8, 4.1, "Amazon ECR", 
                        ["savannah-clinic-api", "• Private container registry", "• Immutable sha256 digests", "• Encrypted storage (AES-256)", "• AppRunnerECRAccessRole", "• Auto-deployment webhook"], 
                        "IMAGE REGISTRY", "docker",
                        bg_color='#FFFFFF', border_color='#FDBA74', badge_color='#EA580C', logo_zoom=0.18)

    # =========================================================================
    # ZONE 4: AWS APP RUNNER (Top Center & Right - Managed Compute)
    # =========================================================================
    draw_zone(5.9, 7.6, 17.0, 4.7, "4. AWS APP RUNNER (FULLY MANAGED CONTAINER COMPUTE)", bg_color='#FFFBEB', border_color='#F59E0B', title_color='#D97706')

    # Sub-component 4A: FastAPI App Gateway
    draw_component_card(6.2, 7.85, 4.9, 4.1, "FastAPI App Gateway", 
                        ["Python 3.12 • Uvicorn ASGI", "• High-throughput async runtime", "• Non-root secure container", "• Pydantic v2 schema validation", "• Correlation ID (X-Request-ID)", "• Live at hf5vyszv5v.awsapprunner.com"], 
                        "API ENTRYPOINT", "fastapi",
                        bg_color='#FFFFFF', border_color='#5EEAD4', badge_color='#009688', logo_zoom=0.18)

    # Sub-component 4B: Dynamic Availability Engine
    draw_component_card(11.45, 7.85, 5.3, 4.1, "Dynamic Availability Engine", 
                        ["30-Minute Dynamic Slot Slicing:", "• Auto-excludes past time windows", "• Excludes booked/confirmed slots", "• Enforces 1-hour booking cutoff", "• Instant slot restoration on cancel", "• Zero disk overhead / compute cached"], 
                        "AVAILABILITY CORE", "python",
                        bg_color='#FFFFFF', border_color='#FCD34D', badge_color='#D97706', logo_zoom=0.18)

    # Sub-component 4C: Atomic Booking Coordinator
    draw_component_card(17.1, 7.85, 5.5, 4.1, "Atomic Booking Coordinator", 
                        ["ACID Concurrency Safety:", "• POST /appointments (201 / 409)", "• Partial Unique Index Enforcement", "• PATCH /cancel with audit reason", "• PATCH /reschedule atomic rollback", "• Upcoming appointments by patient"], 
                        "BOOKING ORCHESTRATOR", "python",
                        bg_color='#FFFFFF', border_color='#FCD34D', badge_color='#D97706', logo_zoom=0.18)

    # =========================================================================
    # ZONE 5: PERSISTENCE LAYER (Bottom Right - Expanded)
    # =========================================================================
    draw_zone(13.4, 2.0, 9.5, 4.8, "5. RELATIONAL PERSISTENCE & CONCURRENCY CONTROL", bg_color='#F0FDF4', border_color='#16A34A', title_color='#15803D')
    
    # Left Card: PostgreSQL ORM Models
    draw_component_card(13.65, 2.25, 4.3, 4.1, "Relational Database", 
                        ["SQLAlchemy 2.0 & PostgreSQL:", "• Doctors & Working Hours", "• Patients & Appointments", "• UTC Datetime Normalization", "• Alembic Migration Scripts", "• Soft-delete via Status Flag"], 
                        "PERSISTENCE CORE", "postgres",
                        bg_color='#FFFFFF', border_color='#86EFAC', badge_color='#336791', logo_zoom=0.18)

    # Right Card: Concurrency Guard (Partial Unique Index)
    draw_component_card(18.25, 2.25, 4.4, 4.1, "Concurrency Engine Lock", 
                        ["ENGINE-LEVEL RACE PREVENTION", "Partial Unique Index Invariant:", "CREATE UNIQUE INDEX ON", "appointments(doctor_id, start_time)", "WHERE status != 'CANCELLED'", "Guarantees ZERO double-bookings", "under concurrent booking requests"], 
                        "DOUBLE-BOOKING GUARD", "postgres",
                        bg_color='#FFFFFF', border_color='#86EFAC', badge_color='#15803D', logo_zoom=0.18)

    # =========================================================================
    # ORTHOGONAL & CLEAN CONNECTION ARROWS
    # =========================================================================
    def draw_orthogonal_arrow(start, end, label, color='#334155', label_pos=None):
        arrow = FancyArrowPatch(start, end, arrowstyle="Simple,tail_width=2.2,head_width=8,head_length=9",
                                color=color, linewidth=2.2, zorder=8)
        ax.add_patch(arrow)
        if label:
            lx = label_pos[0] if label_pos else (start[0] + end[0]) / 2
            ly = label_pos[1] if label_pos else (start[1] + end[1]) / 2
            ax.text(lx, ly, label, fontsize=8.2, fontweight='bold', color=color, ha='center', va='center',
                    bbox=dict(boxstyle="round,pad=0.25", facecolor='#FFFFFF', edgecolor=color, lw=1.2), zorder=9)

    # Arrow 1: Clients -> FastAPI App Gateway (Horizontal)
    draw_orthogonal_arrow((5.3, 9.9), (6.2, 9.9), "1. HTTPS Calls (TLS 1.3)", color='#0284C7', label_pos=(5.75, 10.3))

    # Arrow 2: GitHub Actions -> ECR (Horizontal)
    draw_orthogonal_arrow((8.3, 4.3), (9.05, 4.3), "2. Push Docker Image", color='#24292E', label_pos=(8.68, 4.7))

    # Arrow 3: ECR -> App Runner (Straight UP)
    draw_orthogonal_arrow((11.0, 6.8), (11.0, 7.6), "3. Auto-Deploy Container", color='#EA580C', label_pos=(11.0, 7.2))

    # Arrow 4: App Runner (Coordinator) -> Database (Straight DOWN)
    draw_orthogonal_arrow((18.1, 7.6), (18.1, 6.8), "4. ACID Transactions & Partial Unique Index Lock", color='#15803D', label_pos=(18.1, 7.2))

    # =========================================================================
    # FOOTER: TECHNOLOGY STACK (Logos with names below them - 7 Core Techs)
    # =========================================================================
    footer_bar = FancyBboxPatch((0.8, 0.75), 22.1, 1.05, boxstyle="round,pad=0.06,rounding_size=0.1",
                                facecolor='#F8FAFC', edgecolor='#CBD5E1', linewidth=1.2, zorder=3)
    ax.add_patch(footer_bar)

    ax.text(1.2, 1.28, "TECHNOLOGY STACK ARCHITECTURE:", fontsize=9.5, fontweight='bold', color='#1E293B', va='center', zorder=5)

    tech_stack = [
        ("AWS App Runner", "aws", 0.16),
        ("Amazon ECR", "docker", 0.13),
        ("Terraform (IaC)", "terraform", 0.13),
        ("Python 3.12", "python", 0.13),
        ("FastAPI", "fastapi", 0.13),
        ("PostgreSQL", "postgres", 0.13),
        ("GitHub Actions", "github", 0.13)
    ]

    start_x = 6.2
    spacing = 2.45
    for i, (name, logo_key, z_val) in enumerate(tech_stack):
        cx = start_x + (i * spacing)
        # Logo on top
        add_logo(cx, 1.45, logo_key, zoom=z_val, zorder=6)
        # Name below logo
        ax.text(cx, 0.98, name, fontsize=8.5, fontweight='bold', color='#334155', ha='center', va='center', zorder=6)

    # Document limits & Save
    ax.set_xlim(0, 24)
    ax.set_ylim(0, 14.5)
    ax.axis('off')

    plt.tight_layout(pad=0)
    plt.savefig(output_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close()
    print(f"Architecture diagram generated successfully at: {output_path}")

if __name__ == "__main__":
    create_architecture_diagram()
