/* ─────────────────────────────────────────────────────────
   SocialApp – Main JavaScript
   ───────────────────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {

  // ── CSRF helper ─────────────────────────────────────────
  function getCsrfToken() {
    const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
    return cookie ? cookie.split('=')[1] : '';
  }

  async function postJSON(url, data = {}) {
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: JSON.stringify(data),
    });
    return res.json();
  }

  // ── Toast helper ─────────────────────────────────────────
  function showToast(msg) {
    let toast = document.querySelector('.copy-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.className = 'copy-toast';
      document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2500);
  }

  // ── Like Buttons ─────────────────────────────────────────
  document.querySelectorAll('.like-btn').forEach(btn => {
    btn.addEventListener('click', async function () {
      const postId = this.dataset.postId;
      const url = `/post/${postId}/like/`;

      try {
        const data = await postJSON(url);
        const icon = this.querySelector('i');
        const countEl = this.querySelector('.like-count');

        if (data.liked) {
          icon.className = 'bi bi-heart-fill text-danger';
          this.classList.add('liked');
        } else {
          icon.className = 'bi bi-heart';
          this.classList.remove('liked');
        }

        if (countEl) countEl.textContent = data.count;

        // Animate the heart
        icon.classList.add('heart-pulse');
        icon.addEventListener('animationend', () => icon.classList.remove('heart-pulse'), { once: true });

      } catch (err) {
        console.error('Like failed:', err);
      }
    });
  });

  // ── Follow Buttons ───────────────────────────────────────
  document.querySelectorAll('.follow-btn').forEach(btn => {
    btn.addEventListener('click', async function () {
      const username = this.dataset.username;
      const url = `/profile/${username}/follow/`;

      try {
        const data = await postJSON(url);

        if (data.following) {
          this.textContent = 'Following';
          this.className = 'btn btn-secondary btn-sm follow-btn';
          if (this.dataset.following !== undefined) this.dataset.following = 'true';
        } else {
          this.textContent = 'Follow';
          this.className = 'btn btn-outline-primary btn-sm follow-btn';
          if (this.dataset.following !== undefined) this.dataset.following = 'false';
        }

        // Update follower counts on profile page if present
        const followerCountEl = document.querySelector('.follower-count');
        if (followerCountEl && data.followers_count !== undefined) {
          followerCountEl.textContent = data.followers_count;
        }

      } catch (err) {
        console.error('Follow failed:', err);
      }
    });
  });

  // ── Quick Comment Forms (AJAX) ───────────────────────────
  document.querySelectorAll('.quick-comment-form').forEach(form => {
    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      const postId = this.dataset.postId;
      const input = this.querySelector('input[name="content"]');
      const content = input.value.trim();
      if (!content) return;

      const formData = new FormData(this);
      try {
        const res = await fetch(`/post/${postId}/comment/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest',
          },
          body: formData,
        });

        const data = await res.json();
        if (data.success) {
          input.value = '';

          // If we are on the post detail page, inject the new comment
          const commentsList = document.getElementById('comments-list');
          if (commentsList) {
            const commentHtml = buildCommentHTML(data);
            const emptyMsg = commentsList.querySelector('p.text-center');
            if (emptyMsg) emptyMsg.remove();
            commentsList.insertAdjacentHTML('beforeend', commentHtml);
          }

          // Update comment counts on post cards
          document.querySelectorAll(`#post-${postId} .bi-chat`)
            .forEach(icon => {
              const span = icon.nextElementSibling;
              if (span) span.textContent = data.count;
            });
        }
      } catch (err) {
        console.error('Comment failed:', err);
      }
    });
  });

  function buildCommentHTML(data) {
    const avatarHtml = data.avatar
      ? `<img src="${data.avatar}" class="rounded-circle" width="36" height="36" style="object-fit:cover">`
      : `<div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center fw-bold"
             style="width:36px;height:36px;font-size:14px">${data.author[0].toUpperCase()}</div>`;

    return `
      <div class="comment-thread mb-3" id="comment-${data.comment_id}">
        <div class="d-flex gap-2">
          <a href="/profile/${data.author}/">${avatarHtml}</a>
          <div class="flex-grow-1">
            <div class="bg-light rounded-3 px-3 py-2">
              <div class="d-flex justify-content-between">
                <a href="/profile/${data.author}/" class="fw-semibold text-dark text-decoration-none small">${data.author}</a>
                <span class="text-muted" style="font-size:11px">${data.created_at}</span>
              </div>
              <p class="mb-0 small mt-1">${escapeHtml(data.content)}</p>
            </div>
          </div>
        </div>
      </div>`;
  }

  function escapeHtml(str) {
    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  // ── Copy link buttons ────────────────────────────────────
  document.querySelectorAll('.copy-link-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      const url = this.dataset.url
        ? window.location.origin + this.dataset.url
        : window.location.href;
      navigator.clipboard.writeText(url).then(() => showToast('🔗 Link copied!'));
    });
  });

  // ── Auto-dismiss alerts ──────────────────────────────────
  setTimeout(() => {
    document.querySelectorAll('.alert').forEach(alert => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      bsAlert.close();
    });
  }, 4000);

});
