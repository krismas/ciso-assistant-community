<script lang="ts">
	import {
		Tab,
		TabGroup,
		getModalStore,
		type ModalComponent,
		type ModalSettings,
		type ModalStore
	} from '@skeletonlabs/skeleton';
	import type { ActionData, PageData } from './$types';
	import ActivateTOTPModal from './mfa/components/ActivateTOTPModal.svelte';

	import ConfirmModal from '$lib/components/Modals/ConfirmModal.svelte';
	import { m } from '$paraglide/messages';
	import ListRecoveryCodesModal from './mfa/components/ListRecoveryCodesModal.svelte';
	import { recoveryCodes } from './mfa/utils/stores';

	export let data: PageData;
	export let form: ActionData;

	const modalStore: ModalStore = getModalStore();

	function modalActivateTOTP(totp: Record<string, any>): void {
		const modalComponent: ModalComponent = {
			ref: ActivateTOTPModal,
			props: {
				_form: data.activateTOTPForm,
				formAction: '?/activateTOTP',
				totp
			}
		};
		const modal: ModalSettings = {
			type: 'component',
			component: modalComponent,
			// Data
			title: m.activateTOTPTitle(),
			body: m.activateTOTPMessage()
		};
		modalStore.trigger(modal);
	}

	function modalConfirm(action: string): void {
		const modalComponent: ModalComponent = {
			ref: ConfirmModal,
			props: {
				debug: false,
				formAction: action
			}
		};
		const modal: ModalSettings = {
			type: 'component',
			component: modalComponent,
			// Data
			title: m.confirmModalTitle(),
			body: m.disableTOTPConfirm()
		};
		modalStore.trigger(modal);
	}

	function modalListRecoveryCodes(): void {
		const recoveryCodesModalComponent: ModalComponent = {
			ref: ListRecoveryCodesModal
		};
		const recoveryCodesModal: ModalSettings = {
			type: 'component',
			component: recoveryCodesModalComponent,
			// Data
			title: m.recoveryCodes(),
			body: m.listRecoveryCodesHelpText()
		};
		modalStore.trigger(recoveryCodesModal);
	}

	let tabSet = 0;

	$: hasTOTP = data.authenticators.some((auth) => auth.type === 'totp');
	$: $recoveryCodes =
		form && Object.hasOwn(form, 'recoveryCodes') ? form.recoveryCodes : data.recoveryCodes;
</script>

<TabGroup active="bg-primary-100 text-primary-800 border-b border-primary-800">
	<Tab bind:group={tabSet} name="ssoSettings" value={0}
		><i class="fa-solid fa-shield-halved mr-2" />{m.securitySettings()}</Tab
	>
</TabGroup>
{#if tabSet === 0}
	<div class="p-4 flex flex-col space-y-4">
		<div class="flex flex-col">
			<h3 class="h3 font-medium">{m.securitySettings()}</h3>
			<p class="text-sm text-surface-800">{m.securitySettingsDescription()}</p>
		</div>
		<hr />
		<div class="flow-root">
			<dl class="-my-3 divide-y divide-surface-100 text-sm">
				<div class="grid grid-cols-1 gap-1 py-3 sm:grid-cols-3 sm:gap-4">
					<dt class="font-medium">{m.multiFactorAuthentication()}</dt>
					<dd class="text-surface-900 sm:col-span-2">
						<div class="card p-4 bg-inherit w-fit flex flex-col space-y-3">
							<div class="flex flex-col space-y-2">
								<span class="flex flex-row justify-between text-xl">
									<i class="fa-solid fa-mobile-screen-button"></i>
									{#if hasTOTP}
										<i class="fa-solid fa-circle-check text-success-500-400-token"></i>
									{/if}
								</span>
								<span class="flex flex-row space-x-2">
									<h6 class="h6 text-token">{m.authenticatorApp()}</h6>
									<p class="badge h-fit variant-soft-secondary">{m.recommended()}</p>
								</span>
								<p class="text-sm text-surface-800 max-w-[50ch]">
									{m.authenticatorAppDescription()}
								</p>
							</div>
							<div class="flex flex-wrap justify-between gap-2">
								{#if hasTOTP}
									<button
										class="btn variant-ringed-surface w-fit"
										on:click={(_) => modalConfirm('?/deactivateTOTP')}>{m.disableTOTP()}</button
									>
									{#if data.recoveryCodes}
										<button
											class="btn variant-ringed-surface w-fit"
											on:click={(_) => modalListRecoveryCodes()}>{m.listRecoveryCodes()}</button
										>
									{/if}
								{:else}
									<button
										class="btn variant-ringed-surface w-fit"
										on:click={(_) => modalActivateTOTP(data.totp)}>{m.enableTOTP()}</button
									>
								{/if}
							</div>
						</div>
					</dd>
				</div>
			</dl>
		</div>
	</div>
{/if}
